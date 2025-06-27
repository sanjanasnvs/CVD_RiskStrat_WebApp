from django.core.management.base import BaseCommand
from accounts.models import CVD_Risk_Model_InputFeatures, CVD_Risk_FeatureThresholds
import pandas as pd
import os
import re

class Command(BaseCommand):
    help = 'Load threshold values from Thirds_threshold_values.xlsx by matching base feature names.'

    def handle(self, *args, **kwargs):
        threshold_path = os.path.join('Questionnaire_data', 'Thirds_threshold_values.xlsx')

        try:
            df = pd.read_excel(threshold_path)
        except Exception as e:
            self.stderr.write(f"❌ Error reading Excel: {e}")
            return

        df = df.dropna(subset=["columnName", "threshold"])
        inserted, skipped = 0, 0

        # ---- Step 1: Build lookup dictionary of base_name → feature object from DB ----
        features = CVD_Risk_Model_InputFeatures.objects.all()
        feature_lookup = {}

        for feat in features:
            full_name = feat.feature_name.strip()

            # Remove prefix: category_{category}_ts_
            base_name = re.sub(r"^category_.*?_ts_", "", full_name)
            feature_lookup[base_name] = feat

        # ---- Step 2: Match each threshold row to a base feature and insert ----
        unmatched_in_model = []

        for _, row in df.iterrows():
            base_feature_name = str(row["columnName"]).strip()
            threshold = row["threshold"]

            feature = feature_lookup.get(base_feature_name)

            if not feature:
                unmatched_in_model.append(base_feature_name)
                skipped += 1
                continue

            CVD_Risk_FeatureThresholds.objects.get_or_create(
                feature=feature,
                defaults={"threshold_value": threshold}
            )
            self.stdout.write(f"✅ Inserted threshold for: {feature.feature_name}")
            inserted += 1

        # ---- Step 3: Print out any unmatched base feature names ----
        if unmatched_in_model:
            self.stdout.write("\n⚠️ Threshold file has features not found in DB (even after prefix cleaning):")
            for feat in sorted(unmatched_in_model):
                self.stdout.write(f"   ❌ {feat}")

        self.stdout.write(self.style.SUCCESS(
            f"\n🎯 Completed: {inserted} thresholds inserted, {skipped} skipped."
        ))
