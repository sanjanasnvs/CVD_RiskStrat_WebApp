import pandas as pd
import re
from django.core.management.base import BaseCommand
from accounts.models import (
    CVD_risk_Questionnaire,
    CVD_risk_QuestionnaireDependency
)

class Command(BaseCommand):
    help = "Load conditional question dependencies from Excel (TS_advanced_mapping_v2.xlsx)"

    def handle(self, *args, **kwargs):
        excel_path = "Questionnaire_data/TS_advanced_mapping_v2 (1).xlsx"

        try:
            df = pd.read_excel(excel_path)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Failed to read Excel file: {e}"))
            return

        created, skipped_existing = 0, 0
        skipped_blank, missing_conditional, missing_triggering = 0, 0, 0

        def extract_question_id(raw_val):
            """
            Extracts question ID from strings like 'Q670.0', 'Q6150', etc., using regex.
            Returns an integer or None.
            """
            if pd.isna(raw_val):
                return None
            match = re.search(r"Q?(\d+)", str(raw_val).strip())
            return int(match.group(1)) if match else None

        for index, row in df.iterrows():
            raw_cond_q = row.get("Field.ID")
            cond_q_id = extract_question_id(raw_cond_q)

            if not cond_q_id:
                self.stdout.write(f"⚠️ Row {index + 2}: No conditional question ID found – skipped.")
                skipped_blank += 1
                continue

            try:
                conditional_q = CVD_risk_Questionnaire.objects.get(question_id=cond_q_id)
            except CVD_risk_Questionnaire.DoesNotExist:
                self.stderr.write(f"❌ Row {index + 2} (Q{cond_q_id}): Conditional question NOT FOUND in DB.")
                missing_conditional += 1
                continue

            dependency_set = False

            for col_question, col_answer in [
                ("Determined.by", "Answer"),
                ("Or.determined.by", "Answer.2"),
                ("And.determined.by", "Answer.3")
            ]:
                trig_raw = row.get(col_question)
                trig_q_id = extract_question_id(trig_raw)
                trigger_vals_raw = row.get(col_answer)

                if not trig_q_id or pd.isna(trigger_vals_raw):
                    continue  # Skip empty dependency pair

                try:
                    triggering_q = CVD_risk_Questionnaire.objects.get(question_id=trig_q_id)
                except CVD_risk_Questionnaire.DoesNotExist:
                    self.stderr.write(
                        f"❌ Row {index + 2} (Q{cond_q_id}): Triggering question Q{trig_q_id} not found in DB."
                    )
                    missing_triggering += 1
                    continue

                # Format trigger values as comma-separated string
                trigger_values = [v.strip() for v in str(trigger_vals_raw).split(",") if v.strip()]
                trigger_values_str = ",".join(trigger_values)

                # Check if dependency already exists
                if CVD_risk_QuestionnaireDependency.objects.filter(
                    triggering_question=triggering_q,
                    conditional_question=conditional_q
                ).exists():
                    skipped_existing += 1
                else:
                    CVD_risk_QuestionnaireDependency.objects.create(
                        triggering_question=triggering_q,
                        conditional_question=conditional_q,
                        trigger_values=trigger_values_str
                    )
                    created += 1

                dependency_set = True

            if not dependency_set:
                self.stdout.write(
                    f"ℹ️ Row {index + 2} (Q{cond_q_id}): Question found but no dependencies defined in this row."
                )

        # Summary
        self.stdout.write("\n========== LOAD SUMMARY ==========")
        self.stdout.write(f"✅ Created new dependencies: {created}")
        self.stdout.write(f"⚠️ Skipped (already existed): {skipped_existing}")
        self.stdout.write(f"⚠️ Skipped rows with blank Field.ID: {skipped_blank}")
        self.stdout.write(f"❌ Conditional questions NOT FOUND in DB: {missing_conditional}")
        self.stdout.write(f"❌ Triggering questions NOT FOUND in DB: {missing_triggering}")
        self.stdout.write("==================================\n")
