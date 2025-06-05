import pandas as pd
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import CVD_risk_Questionnaire, CVD_risk_QuestionResponseOptions


class Command(BaseCommand):
    help = 'Load question response options into CVD_risk_QuestionResponseOptions table.'

    def handle(self, *args, **kwargs):
        # Load Excel
        data_dir = os.path.join(settings.BASE_DIR, 'Questionnaire_data')
        file_path = os.path.join(data_dir, 'TS_mapping_with_questions_v1.xlsx')

        print("📄 Loading Excel file...")
        df = pd.read_excel(file_path)
        df.columns = df.columns.str.strip()

        # Filter rows that have answers and valid Field IDs
        option_rows = df[df['Full Answer'].notna() & df['Field ID'].notna()].copy()
        option_rows['Field ID'] = option_rows['Field ID'].astype(int)

        # Clean question IDs actually in DB
        valid_qids = set(CVD_risk_Questionnaire.objects.values_list('question_id', flat=True))
        option_rows = option_rows[option_rows['Field ID'].isin(valid_qids)]

        # Extract answer value and text
        option_rows[['value', 'option_text']] = option_rows['Full Answer'].str.extract(r'([-\d.]+)\s*:\s*(.*)')
        option_rows = option_rows.dropna(subset=['value', 'option_text'])

        created, skipped = 0, 0

        print("💾 Inserting options into database...")
        for _, row in option_rows.iterrows():
            try:
                qid = int(row['Field ID'])
                question = CVD_risk_Questionnaire.objects.get(question_id=qid)

                # Clear existing options for this question (optional safety net)
                # CVD_risk_QuestionResponseOptions.objects.filter(question=question).delete()

                option_label = str(row.get('Select one/Toggle multiple/Enter integer answer', '')).strip()

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

