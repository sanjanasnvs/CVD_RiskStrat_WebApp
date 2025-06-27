import pandas as pd
import re
from django.core.management.base import BaseCommand
from accounts.models import (
    FeatureOptionMapping,
    CVD_Risk_Model_InputFeatures,
    CVD_risk_QuestionResponseOptions,
)

class Command(BaseCommand):
    help = "Populate FeatureOptionMapping table from TS_mapping_with_questions_v1.xlsx"

    def add_arguments(self, parser):
        parser.add_argument(
            "excel_path",
            type=str,
            help="Path to Excel file with columns: 'Column names' and 'Full Answer'"
        )

    def handle(self, *args, **options):
        path = options["excel_path"]

        # Load the Excel file
        try:
            df = pd.read_excel(path)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Failed to read Excel: {e}"))
            return

        # Ensure required columns are present
        required_cols = ["Column names", "Full Answer"]
        if not all(col in df.columns for col in required_cols):
            self.stderr.write(self.style.ERROR(f"❌ Missing required columns: {required_cols}"))
            return

        created, skipped = 0, 0

        for _, row in df.iterrows():
            feature_name = str(row["Column names"]).strip()
            raw_answer = row["Full Answer"]

            # Skip numeric features with no answer mappings
            if pd.isna(raw_answer):
                self.stdout.write(f"⏭️ Skipping missing answer (likely numeric): {feature_name}")
                continue

            # Remove any numeric prefix like "1: " or "-7: " from the answer
            cleaned_answer = re.sub(r"^\s*-?\d+\s*[:：]\s*", "", str(raw_answer)).strip()

            try:
                # Make sure feature exists in DB (our canonical list)
                try:
                    feature = CVD_Risk_Model_InputFeatures.objects.get(feature_name=feature_name)
                except CVD_Risk_Model_InputFeatures.DoesNotExist:
                    self.stdout.write(f"⏭️ Feature not in final DB: {feature_name}")
                    continue

                question = feature.question

                # Fetch options matching this answer text under the same question only
                options_qs = CVD_risk_QuestionResponseOptions.objects.filter(
                    question=question,
                    option_text__iexact=cleaned_answer
                )

                match_count = options_qs.count()

                if match_count == 0:
                    self.stderr.write(f"❌ Option not found: '{cleaned_answer}' (Feature: {feature_name}, QID: {question.question_id})")
                    continue
                elif match_count == 1:
                    option = options_qs.first()
                else:
                    self.stderr.write(f"⚠️ Duplicate warning: Multiple options found for '{cleaned_answer}' (Feature: {feature_name}, QID: {question.question_id}) – using first match")
                    option = options_qs.first()

                # Create mapping only if it doesn't already exist
                _, created_flag = FeatureOptionMapping.objects.get_or_create(
                    feature_name=feature_name,
                    question=question,
                    option=option
                )

                if created_flag:
                    created += 1
                    self.stdout.write(self.style.SUCCESS(f"✅ Mapped: {feature_name} → '{cleaned_answer}'"))
                else:
                    skipped += 1
                    self.stdout.write(f"⏭️ Already exists: {feature_name}")

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"❌ Unexpected error for {feature_name}: {e}"))

        # Final summary
        self.stdout.write("\n📊 Summary")
        self.stdout.write(f"✅ Mappings created: {created}")
        self.stdout.write(f"⏭️ Skipped or already present: {skipped}")
