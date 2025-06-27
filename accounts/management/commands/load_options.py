import pandas as pd
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import CVD_risk_Questionnaire, CVD_risk_QuestionResponseOptions


class Command(BaseCommand):
    help = 'Load question response options into CVD_risk_QuestionResponseOptions table.'

    def handle(self, *args, **kwargs):
        # Define path to the Excel file
        data_dir = os.path.join(settings.BASE_DIR, 'Questionnaire_data')
        file_path = os.path.join(data_dir, 'TS_mapping_with_questions_v1.xlsx')

        print("📄 Loading Excel file...")
        df = pd.read_excel(file_path)
        df.columns = df.columns.str.strip()  # Remove any extra whitespace from column names

        # Filter only rows with answers and valid question IDs (Field ID)
        option_rows = df[df['Full Answer'].notna() & df['Field ID'].notna()].copy()
        option_rows['Field ID'] = option_rows['Field ID'].astype(int)

        # Restrict to questions that are actually present in the DB
        valid_qids = set(CVD_risk_Questionnaire.objects.values_list('question_id', flat=True))
        option_rows = option_rows[option_rows['Field ID'].isin(valid_qids)]

        # Split 'Full Answer' column like "1 : Option Text" into two parts
        option_rows[['value', 'option_text']] = option_rows['Full Answer'].str.extract(r'([-\d.]+)\s*:\s*(.*)')
        option_rows = option_rows.dropna(subset=['value', 'option_text'])  # Drop rows if extraction failed

        created, skipped, deleted_questions = 0, 0, set()

        print("💾 Inserting options into database...")
        for _, row in option_rows.iterrows():
            try:
                qid = int(row['Field ID'])
                question = CVD_risk_Questionnaire.objects.get(question_id=qid)

                # ⚠️ Only delete once per question to avoid repeated deletes
                if qid not in deleted_questions:
                    CVD_risk_QuestionResponseOptions.objects.filter(question=question).delete()
                    deleted_questions.add(qid)
                    print(f"🧹 Cleared old options for Q{qid}")

                # Optional label field from the Excel, may be blank
                option_label = str(row.get('Select one/Toggle multiple/Enter integer answer', '')).strip()

                # Insert the cleaned response option
                CVD_risk_QuestionResponseOptions.objects.create(
                    question=question,
                    option_text=row['option_text'].strip(),
                    option_label=option_label,
                    encoded_value=float(row['value']),
                )

                print(f"✅ Added option for Q{qid}: {row['option_text'].strip()}")
                created += 1

            except Exception as e:
                print(f"❌ Error with Q{row.get('Field ID')} – {e}")
                skipped += 1

        # Final summary
        print(f"\n✅ Total options created: {created}")
        print(f"❌ Total rows skipped: {skipped}")
        print(f"🧹 Cleared old options for {len(deleted_questions)} questions")

