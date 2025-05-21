import pandas as pd
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import CVD_risk_Questionnaire


class Command(BaseCommand):
    help = 'Load questions and dependencies into CVD_risk_Questionnaire table using ManyToManyField.'

    def handle(self, *args, **kwargs):
        # Setup paths
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(settings.BASE_DIR, 'Questionnaire_data')

        questions_file = os.path.join(data_dir, 'TS_mapping_with_questions_v1.xlsx')
        dependencies_file = os.path.join(data_dir, 'TS_advanced_mapping_v2 (1).xlsx')

        print("🔄 Loading Excel files...")
        mapping_df = pd.read_excel(questions_file)
        advanced_df = pd.read_excel(dependencies_file)

        # Clean headers
        mapping_df.columns = mapping_df.columns.str.strip()
        advanced_df.columns = advanced_df.columns.str.strip()

        print("🧹 Clearing existing questions...")
        CVD_risk_Questionnaire.objects.all().delete()

        print("🔗 Deduplicating and merging files...")
        unique_questions_df = mapping_df.drop_duplicates(subset=["Field ID"])
        merged_df = pd.merge(unique_questions_df, advanced_df, how='left', left_on='Field ID', right_on='Field.ID')

        imported, skipped, duplicates = 0, 0, 0
        seen_ids = set()
        question_lookup = {}

        print("📥 Inserting questions...")

        for idx, row in merged_df.iterrows():
            field_id = row.get('Field ID')
            question_text = row.get('Question Stem')
            category = row.get('Category')
            subcategory = row.get('Sub.category')
            question_order = idx + 1

            if pd.isna(field_id) or pd.isna(question_text):
                skipped += 1
                continue

            try:
                question_id = int(float(field_id))
            except ValueError:
                skipped += 1
                continue

            if question_id in seen_ids:
                duplicates += 1
                continue

            try:
                q = CVD_risk_Questionnaire.objects.create(
                    question_id=question_id,
                    question_text=str(question_text).strip(),
                    category=str(category).strip() if isinstance(category, str) else None,
                    subcategory=str(subcategory).strip() if isinstance(subcategory, str) else None,
                    question_order=question_order
                )
                question_lookup[question_id] = q
                seen_ids.add(question_id)
                imported += 1
            except Exception as e:
                print(f"❌ Error importing row {idx} (Field ID: {field_id}): {e}")
                skipped += 1

        print(f"\n✅ Imported {imported} questions.")
        print(f"❌ Skipped {skipped} rows. 🔁 Ignored {duplicates} duplicates.")

        # ✅ Dependency update block
        print("\n🔄 Updating dependencies...")

        advanced_df["Has_Dep"] = advanced_df[["Determined.by", "Or.determined.by", "And.determined.by"]].notna().any(axis=1)
        filtered_dependencies_df = advanced_df.sort_values("Has_Dep", ascending=False).drop_duplicates(subset=["Field.ID"])

        updated = 0

        for _, row in filtered_dependencies_df.iterrows():
            try:
                question_id = int(float(row.get("Field.ID")))
                q = question_lookup.get(question_id)
                if not q:
                    continue
            except (TypeError, ValueError):
                continue

            deps = []
            for dep_col in ['Determined.by', 'Or.determined.by', 'And.determined.by']:
                val = row.get(dep_col)
                if pd.notna(val):
                    dep_str = str(val)
                    deps.extend([
                        str(int(float(d.strip())))
                        for d in dep_str.split(',')
                        if d.strip().lstrip('-').replace('.', '', 1).isdigit()
                    ])

            if deps:
                dependency_objs = CVD_risk_Questionnaire.objects.filter(question_id__in=[int(d) for d in deps])
                q.dependencies.set(dependency_objs)
                updated += 1
            else:
                q.dependencies.clear()

        print(f"🔗 Updated {updated} questions with dependencies.")

