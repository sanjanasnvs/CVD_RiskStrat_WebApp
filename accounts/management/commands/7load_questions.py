import pandas as pd
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import CVD_risk_Questionnaire, CVD_risk_QuestionnaireDependency

class Command(BaseCommand):
    help = 'Load filtered and ordered CVD risk questions and dependencies into the database.'

    def handle(self, *args, **kwargs):
        CATEGORY_ORDER = [
            "Sociodemographics", "Health and medical history", "Sex-specific factors",
            "Early life factors", "Family History", "Lifestyle and environment", "Psychosocial factors"
        ]
        category_index = {cat: i for i, cat in enumerate(CATEGORY_ORDER)}

        # Set file paths
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(settings.BASE_DIR, 'Questionnaire_data')
        questions_file = os.path.join(data_dir, 'TS_mapping_with_questions_v1.xlsx')
        dependencies_file = os.path.join(data_dir, 'TS_advanced_mapping_v2 (1).xlsx')
        sample_file = os.path.join(settings.BASE_DIR, 'model_files', 'sociodemographicsSample (1).csv')

        print("🔄 Loading files...")

        # Extract used column names from sample CSV — strip the known prefix
        used_columns = pd.read_csv(sample_file, header=None)[0].str.replace(
            'category_Sociodemographics_ts_', '', regex=False
        ).tolist()

        # Load Excel files
        mapping_df = pd.read_excel(questions_file)
        advanced_df = pd.read_excel(dependencies_file)

        # Clean column headers
        mapping_df.columns = mapping_df.columns.str.strip()
        advanced_df.columns = advanced_df.columns.str.strip()

        print("🧹 Clearing existing questions and dependencies...")
        CVD_risk_Questionnaire.objects.all().delete()
        CVD_risk_QuestionnaireDependency.objects.all().delete()

        # Filter questions to only those in the sample CSV
        mapping_df = mapping_df[mapping_df['Column names'].isin(used_columns)]

        # Remove duplicate Field IDs
        unique_questions_df = mapping_df.drop_duplicates(subset=["Field ID"])

        # Merge with dependencies and add category ordering
        merged_df = pd.merge(unique_questions_df, advanced_df, how='left', left_on='Field ID', right_on='Field.ID')
        merged_df['CategoryOrder'] = merged_df['Category'].map(category_index)
        merged_df = merged_df.sort_values(by=['CategoryOrder', 'Field ID'])

        print("📥 Inserting filtered questions...")
        question_lookup = {}
        seen_ids = set()
        imported = skipped = duplicates = 0

        for question_order, (_, row) in enumerate(merged_df.iterrows(), start=1):
            try:
                question_id = int(float(row.get('Field ID')))
                if question_id in seen_ids:
                    duplicates += 1
                    continue

                question = CVD_risk_Questionnaire.objects.create(
                    question_id=question_id,
                    question_text=str(row.get('Question Stem')).strip(),
                    category=str(row.get('Category')).strip() if pd.notna(row.get('Category')) else None,
                    subcategory=str(row.get('Sub.category')).strip() if pd.notna(row.get('Sub.category')) else None,
                    question_order=question_order,
                    answer_type=str(row.get('Select one/Toggle multiple/Enter integer answer')).strip()
                    if pd.notna(row.get('Select one/Toggle multiple/Enter integer answer')) else None
                )
                question_lookup[question_id] = question
                seen_ids.add(question_id)
                imported += 1
            except Exception as e:
                print(f"❌ Failed to import question: {e}")
                skipped += 1

        print(f"✅ Imported {imported} questions. ❌ Skipped {skipped}. 🔁 Duplicates ignored: {duplicates}")

        print("🔗 Inserting dependencies with trigger values...")
        dependency_count = 0
        seen_pairs = set()

        for _, row in advanced_df.iterrows():
            to_qid_raw = row.get('Field.ID')
            if pd.isna(to_qid_raw): continue

            try:
                to_qid = int(float(to_qid_raw))
                to_question = question_lookup.get(to_qid)
                if not to_question: continue
            except Exception:
                continue

            dependency_map = {
                'Determined.by': 'Answer',
                'Or.determined.by': 'Answer.2',
                'And.determined.by': 'Answer.3'
            }

            for dep_col, ans_col in dependency_map.items():
                dep_ids_raw = row.get(dep_col)
                trigger_raw = row.get(ans_col)

                if pd.isna(dep_ids_raw) or pd.isna(trigger_raw):
                    continue

                trigger_values = [
                    int(float(val.strip())) for val in str(trigger_raw).split(',')
                    if val.strip().lstrip('-').replace('.', '', 1).isdigit()
                ]

                for dep_id in str(dep_ids_raw).split(','):
                    try:
                        from_qid = int(float(dep_id.strip()))
                        from_question = question_lookup.get(from_qid)
                        if not from_question: continue

                        pair_key = (from_qid, to_qid)
                        if pair_key in seen_pairs:
                            continue
                        seen_pairs.add(pair_key)

                        CVD_risk_QuestionnaireDependency.objects.create(
                            triggering_question=from_question,
                            conditional_question=to_question,
                            trigger_values=trigger_values
                        )
                        dependency_count += 1
                    except Exception:
                        continue

        print(f"🔗 Created {dependency_count} new dependencies with trigger values.")
        print(f"🔁 Skipped {len(seen_pairs) - dependency_count} duplicate dependencies.")

