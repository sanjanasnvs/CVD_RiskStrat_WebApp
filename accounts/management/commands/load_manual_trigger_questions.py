from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import CVD_risk_Questionnaire, CVD_risk_QuestionResponseOptions

import os
import pandas as pd


class Command(BaseCommand):
    help = "Manually loads specific trigger questions and their options needed only for conditional logic."

    def handle(self, *args, **kwargs):
        # ✅ Question IDs to insert manually (not model inputs but required for conditional logic)
        manual_qids = {884, 1767, 2365}

        # 📁 Load Excel mapping file
        excel_path = os.path.join(settings.BASE_DIR, 'Questionnaire_data', 'TS_mapping_with_questions_v1.xlsx')
        try:
            df = pd.read_excel(excel_path)
            df.columns = df.columns.str.strip()
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Failed to read Excel file: {e}"))
            return

        # 🎯 Filter for valid and relevant rows
        df = df[df['Field ID'].notna()]
        df['Field ID'] = df['Field ID'].astype(int)
        question_rows = df[df['Field ID'].isin(manual_qids)]

        inserted_qs = 0
        created_opts = 0
        skipped_opts = 0

        # --------------------------------
        # STEP 1: Insert or Update Questions
        # --------------------------------
        for qid in manual_qids:
            rows = question_rows[question_rows['Field ID'] == qid]
            if rows.empty:
                self.stdout.write(self.style.WARNING(f"⚠️ Q{qid} not found in Excel. Skipped."))
                continue

            question_row = rows.iloc[0]
            try:
                question, created = CVD_risk_Questionnaire.objects.update_or_create(
                    question_id=qid,
                    defaults={
                        'question_text': str(question_row.get('Question Stem', '')).strip(),
                        'category': str(question_row.get('Category', '')).strip(),
                        'subcategory': str(question_row.get('Sub.category', '')).strip()
                            if pd.notna(question_row.get('Sub.category')) else None,
                        'answer_type': str(question_row.get('Select one/Toggle multiple/Enter integer answer', '')).strip(),
                        'question_order': 999  # Arbitrary end-order
                    }
                )
                msg = f"✅ Inserted Q{qid}" if created else f"🔁 Updated Q{qid}"
                self.stdout.write(self.style.SUCCESS(f"{msg}: {question.question_text}"))
                inserted_qs += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"❌ Failed to insert Q{qid}: {e}"))

        # --------------------------------
        # STEP 2: Insert Options
        # --------------------------------
        for qid in manual_qids:
            rows = question_rows[question_rows['Field ID'] == qid]
            if rows.empty:
                continue

            try:
                question = CVD_risk_Questionnaire.objects.get(question_id=qid)

                # 🧹 Clear existing options
                CVD_risk_QuestionResponseOptions.objects.filter(question=question).delete()

                for _, row in rows.iterrows():
                    full_answer = str(row.get('Full Answer', '')).strip()
                    if not full_answer or ':' not in full_answer:
                        skipped_opts += 1
                        continue
                    try:
                        val, text = full_answer.split(":", 1)
                        CVD_risk_QuestionResponseOptions.objects.create(
                            question=question,
                            option_text=text.strip(),
                            encoded_value=float(val.strip()),
                            option_label=str(row.get('Select one/Toggle multiple/Enter integer answer', '')).strip()
                        )
                        created_opts += 1
                    except Exception as e:
                        skipped_opts += 1
                        self.stderr.write(self.style.ERROR(
                            f"❌ Skipped option for Q{qid} due to parse error: {e}"))

                self.stdout.write(self.style.SUCCESS(f"✅ Options inserted for Q{qid}"))

            except CVD_risk_Questionnaire.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"❌ Q{qid} not found in DB – options not inserted"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"❌ Failed to insert options for Q{qid}: {e}"))

        # ✅ Final Summary
        self.stdout.write("\n========== SUMMARY ==========")
        self.stdout.write(f"✅ Questions inserted/updated: {inserted_qs}")
        self.stdout.write(f"✅ Options inserted: {created_opts}")
        self.stdout.write(f"⚠️ Options skipped: {skipped_opts}")
        self.stdout.write("=============================\n")
