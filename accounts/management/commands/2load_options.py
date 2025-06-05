import pandas as pd
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import CVD_risk_Questionnaire, CVD_risk_QuestionResponseOptions


class Command(BaseCommand):
    help = 'Load question response options into CVD_risk_QuestionResponseOptions table.'

    def handle(self, *args, **kwargs):
        # 1. Load the Excel file
        data_dir = os.path.join(settings.BASE_DIR, 'Questionnaire_data')
        file_path = os.path.join(data_dir, 'TS_mapping_with_questions_v1.xlsx')

        print("📄 Loading Excel file...")
        df = pd.read_excel(file_path)
        df.columns = df.columns.str.strip()

        # 2. Filter valid option rows (only MCQ questions)
        option_rows = df[df['Full Answer'].notna()].copy()
        option_rows = option_rows[option_rows['Field ID'].notna()]
        option_rows['Field ID'] = option_rows['Field ID'].astype(int)

        # 3. Extract values from "Full Answer" column (e.g. '1 : Yes')
        option_rows[['value', 'option_text']] = option_rows['Full Answer'].str.extract(r'([-\d]+)\s*:\s*(.*)')

        valid_options_df = option_rows.dropna(subset=['value', 'option_text'])

        created, skipped = 0, 0

        print("💾 Inserting options into database...")
        for _, row in valid_options_df.iterrows():
            try:
                qid = int(row['Field ID'])
                question = CVD_risk_Questionnaire.objects.filter(question_id=qid).first()

                if not question:
                    print(f"⚠️ Skipping: Question ID {qid} not found in DB.")
                    skipped += 1
                    continue

                # Strip label for answer_type field
                option_label = str(row.get('Select one/Toggle multiple/Enter integer answer', '')).strip()

                # Create option
                CVD_risk_QuestionResponseOptions.objects.create(
                    question=question,
                    option_text=row['option_text'].strip(),
                    option_label=option_label,
                    value_range_start=float(row['value']),
                    value_range_end=float(row['value'])
                )
                print(f"✅ Added option for Q{qid}: {row['option_text'].strip()}")
                created += 1

            except Exception as e:
                print(f"❌ Error with Q{row.get('Field ID')} – {e}")
                skipped += 1

        print(f"\n✅ Created {created} options.")
        print(f"❌ Skipped {skipped} rows.")

