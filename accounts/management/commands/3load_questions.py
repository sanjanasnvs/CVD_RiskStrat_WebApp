import pandas as pd
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import CVD_risk_Questionnaire, CVD_risk_QuestionResponseOptions

# Define file locations
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(settings.BASE_DIR, 'Questionnaire_data')
QUESTIONS_FILE = os.path.join(DATA_DIR, 'TS_mapping_with_questions_v1.xlsx')
DEPENDENCIES_FILE = os.path.join(DATA_DIR, 'TS_advanced_mapping_v2 (1).xlsx')


class Command(BaseCommand):
    help = 'Load questions with category, subcategory, and dependencies into CVD_risk_Questionnaire table.'

    def handle(self, *args, **kwargs):
        # Load both Excel files
        print("Loading Excel files...")
        mapping_df = pd.read_excel('Questionnaire_data/TS_mapping_with_questions_v1.xlsx')
        advanced_df = pd.read_excel('Questionnaire_data/TS_advanced_mapping_v2 (1).xlsx')

        # Clean headers
        mapping_df.columns = mapping_df.columns.str.strip()
        advanced_df.columns = advanced_df.columns.str.strip()

        # Merge both files on 'Field.ID'
        print("Merging data sources...")
        merged_df = pd.merge(mapping_df, advanced_df, how='left', left_on='Field ID', right_on='Field.ID')

        # Step 1: Load base questions
        print("Creating base questions with category/subcategory...")
        CVD_risk_Questionnaire.objects.all().delete()  # Optional: clear table before reloading

        imported, skipped = 0, 0
        for _, row in merged_df.iterrows():
            question_text = row.get('Question')
            question_order = row.get('Question No')

            if pd.isna(question_text) or pd.isna(question_order):
                skipped += 1
                continue

            try:
                question_order = int(float(question_order))
            except ValueError:
                skipped += 1
                continue

            category = row.get('Category')
            subcategory = row.get('Sub.category')

            CVD_risk_Questionnaire.objects.create(
                question_text=question_text.strip(),
                question_order=question_order,
                category=category.strip() if isinstance(category, str) else None,
                subcategory=subcategory.strip() if isinstance(subcategory, str) else None
            )
            imported += 1

        print(f" Imported {imported} questions. Skipped {skipped} blank or invalid rows.")

        # Step 2: Populate dependencies
        print("Updating dependency fields...")
        updated = 0
        for _, row in advanced_df.iterrows():
            raw_qid = row.get('Field.ID')
            try:
                question_order = int(float(raw_qid))
            except (TypeError, ValueError):
                continue

            try:
                q = CVD_risk_Questionnaire.objects.get(question_order=question_order)
            except CVD_risk_Questionnaire.DoesNotExist:
                continue

            deps = []
            for dep_col in ['Determined.by', 'Or.determined.by', 'And.determined.by']:
                ids = row.get(dep_col)
                if isinstance(ids, str):
                    deps.extend([d.strip() for d in ids.split(',') if d.strip().lstrip('-').isdigit()])

            q.dependencies = ",".join(deps) if deps else None
            q.save()
            updated += 1

        print(f" Updated {updated} questions with dependencies.")

