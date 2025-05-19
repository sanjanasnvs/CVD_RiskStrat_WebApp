import pandas as pd
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import CVD_risk_Questionnaire, CVD_risk_QuestionResponseOptions


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(settings.BASE_DIR, 'Questionnaire_data')
QUESTIONS_FILE = os.path.join(DATA_DIR, 'TS_mapping_with_questions_v1.xlsx')

class Command(BaseCommand):
    help = 'Load questionnaire questions and options into the database'

    def handle(self, *args, **kwargs):
        df = pd.read_excel(QUESTIONS_FILE)

        created_questions = 0
        skipped_rows = 0

        for _, row in df.iterrows():
            question_text = row.get('Question Stem')
            column_name = row.get('Column names')
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

            if data_type in ['categorical', 'binary'] and not pd.isna(row.get('Full Answer')):
                answers = str(row['Full Answer']).split(';')
                for ans in answers:
                    CVD_risk_QuestionResponseOptions.objects.create(
                        question=question,
                        option_text=ans.strip()
                    )

        self.stdout.write(self.style.SUCCESS(
            f'Imported {created_questions} questions. Skipped {skipped_rows} blank rows.'
        ))

