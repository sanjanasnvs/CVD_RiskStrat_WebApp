from django.core.management.base import BaseCommand
from accounts.models import (
    CVD_risk_Questionnaire,
    CVD_risk_QuestionnaireDependency
)
from django.conf import settings
import pandas as pd
import os

class Command(BaseCommand):
    help = "Insert Q31-based dependencies only for questions that exist in the DB"

    def handle(self, *args, **kwargs):
        filepath = os.path.join(settings.BASE_DIR, 'Questionnaire_data', 'TS_advanced_mapping_v2 (1).xlsx')

        try:
            df = pd.read_excel(filepath)
            df.columns = df.columns.str.strip()
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Failed to read Excel: {e}"))
            return

        df = df[df['Determined.by'] == 31]
        inserted_count = 0

        for _, row in df.iterrows():
            raw_qid = row['Field.ID']
            raw_ans = row['Answer']

            if pd.isna(raw_qid) or pd.isna(raw_ans):
                continue

            try:
                conditional_qid = int(float(raw_qid))
                trigger_val = str(int(float(raw_ans)))  # 0 or 1
                trigger_label = 'Female' if trigger_val == '0' else 'Male' if trigger_val == '1' else None

                if not trigger_label:
                    continue

                # ✅ Skip if conditional question not in DB
                if not CVD_risk_Questionnaire.objects.filter(question_id=conditional_qid).exists():
                    print(f"⚠️ Skipped: Q{conditional_qid} does not exist")
                    continue

                # ✅ Create dependency if not exists
                dependency_obj, created = CVD_risk_QuestionnaireDependency.objects.get_or_create(
                    triggering_question_id=31,
                    conditional_question_id=conditional_qid
                )
                if created:
                    print(f"🆕 Created Dependency: Q31 → Q{conditional_qid}")

                # ✅ Add or update trigger values
                values_obj, _ = CVD_risk_QuestionnaireDependencyValues.objects.update_or_create(
                    triggering_question_id=31,
                    conditional_question_id=conditional_qid,
                    defaults={"trigger_values": trigger_label}
                )

                print(f"✅ Set Trigger: Q31 → Q{conditional_qid} for '{trigger_label}'")
                inserted_count += 1

            except Exception as err:
                print(f"❌ Failed for Q{raw_qid}: {err}")

        print(f"\n✅ Total inserted/updated: {inserted_count}")
