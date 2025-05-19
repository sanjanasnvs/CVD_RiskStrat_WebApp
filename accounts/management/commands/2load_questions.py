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
    help = 'Load and update questionnaire data including dependencies, category, and subcategory.'

    def handle(self, *args, **kwargs):
        # Step 1: Load main question mapping
        df_questions = pd.read_excel(QUESTIONS_FILE)
        created_questions = 0
        skipped_rows = 0

        self.stdout.write("Creating base questions with category/subcategory...")

        for _, row in df_questions.iterrows():
            question_text = row.get('Question Stem')
            response_type = str(row.get('Select one/Toggle multiple/Enter integer answer', '')).lower()
            data_type = str(row.get('Data type', '')).lower()
            category = row.get('Category', None)
            subcategory = row.get('Sub-category', None)

            if pd.isna(question_text):
                skipped_rows += 1
                continue

            question = CVD_risk_Questionnaire.objects.create(
                question_text=question_text.strip(),
                category=category,
                subcategory=subcategory,
                question_order=int(row.name) + 1
            )
            created_questions += 1

            # Create response options for categorical/binary
            if data_type in ['categorical', 'binary'] and not pd.isna(row.get('Full Answer')):
                answers = str(row['Full Answer']).split(';')
                for ans in answers:
                    CVD_risk_QuestionResponseOptions.objects.create(
                        question=question,
                        option_text=ans.strip()
                    )

        self.stdout.write(self.style.SUCCESS(f'Imported {created_questions} questions. Skipped {skipped_rows} blank rows.'))

        # Step 2: Load advanced dependency file
        self.stdout.write("Updating dependency fields...")
        df_deps = pd.read_excel(DEPENDENCIES_FILE)

        updated = 0
        for idx, row in df_deps.iterrows():
            qid = row.get('Question No')

            if pd.isna(qid):
                continue  # Skip rows without a Question No

            deps = []

            for col in ['Determined.by', 'Or.determined.by', 'And.determined.by']:
                val = row.get(col)
                if not pd.isna(val):
                    parts = [p.strip() for p in str(val).split(',') if p.strip()]
                    deps.extend(parts)

            if deps:
                try:
                    q = CVD_risk_Questionnaire.objects.get(question_order=int(qid))
                    q.dependencies = ','.join(deps)
                    q.save()
                    updated += 1
                except CVD_risk_Questionnaire.DoesNotExist:
                    self.stdout.write(f"Question {qid} not found in DB.")

        self.stdout.write(self.style.SUCCESS(f'Updated {updated} questions with dependencies.'))

