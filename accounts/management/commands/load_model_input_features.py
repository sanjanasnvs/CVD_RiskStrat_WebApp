from django.core.management.base import BaseCommand
from accounts.models import CVD_Risk_Model_InputFeatures, CVD_risk_Questionnaire
import pandas as pd
import os
import re

class Command(BaseCommand):
    help = 'Load model input features from final sample CSV using question mappings.'

    def handle(self, *args, **kwargs):
        # === Step 1: Load the CSV and mapping Excel ===
        sample_csv = os.path.join('model_files', 'Input features sample files', 'biggestModelnoDropSample.csv')
        mapping_excel = os.path.join('Questionnaire_data', 'TS_mapping_with_questions_v1.xlsx')

        try:
            feature_df = pd.read_csv(sample_csv, header=None, skiprows=1)
        except Exception as e:
            self.stderr.write(f"❌ Could not read sample CSV: {e}")
            return

        try:
            map_df = pd.read_excel(mapping_excel)
        except Exception as e:
            self.stderr.write(f"❌ Could not read mapping Excel: {e}")
            return

        # === Step 2: Build column-to-FieldID mapping ===
        map_df = map_df.dropna(subset=['Field ID', 'Column names'])
        mapping_dict = dict(zip(map_df['Column names'].astype(str).str.strip(), map_df['Field ID'].astype(int)))

        created, skipped = 0, 0

        for _, row in feature_df.iterrows():
            full_feature_name = str(row[0]).strip()

            # Remove ONLY the prefix category_{...}_ts_
            cleaned_feature = re.sub(r'^category_.*?_ts_', '', full_feature_name)

            question_id = mapping_dict.get(cleaned_feature)

            if not question_id:
                self.stderr.write(f"⚠️ No mapping found for: {cleaned_feature}")
                skipped += 1
                continue

            try:
                question = CVD_risk_Questionnaire.objects.get(question_id=question_id)
            except CVD_risk_Questionnaire.DoesNotExist:
                self.stderr.write(f"⚠️ Question ID {question_id} not found in DB")
                skipped += 1
                continue

            # Insert into DB
            _, created_flag = CVD_Risk_Model_InputFeatures.objects.get_or_create(
                question=question,
                feature_name=full_feature_name,
            )

            if created_flag:
                self.stdout.write(f"✅ Created feature: {full_feature_name}")
                created += 1
            else:
                self.stdout.write(f"⏭️ Already exists: {full_feature_name}")
                skipped += 1

        self.stdout.write(self.style.SUCCESS(f"\n🎯 Completed: {created} features created, {skipped} skipped."))

