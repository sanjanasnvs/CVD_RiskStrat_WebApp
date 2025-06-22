# accounts/management/commands/load_encoded_options.py

from django.core.management.base import BaseCommand
from accounts.models import (
    CVD_Risk_Model_InputFeatures,
    CVD_risk_QuestionResponseOptions,
)
from difflib import SequenceMatcher


class Command(BaseCommand):
    help = "Auto-populate encoded_option field in model input features using matching option_text from response options."

    def handle(self, *args, **kwargs):
        updated_count = 0
        skipped_count = 0

        # Fetch all model features where encoded_option has not been set
        features = CVD_Risk_Model_InputFeatures.objects.filter(encoded_option__isnull=True)
        total = features.count()
        self.stdout.write(f"🔍 Processing {total} features missing encoded_option...\n")

        for feature in features:
            try:
                # Pull all possible response options for this feature's linked question
                options = CVD_risk_QuestionResponseOptions.objects.filter(question=feature.question)

                if not options.exists():
                    self.stdout.write(self.style.WARNING(f"⚠️ No options found for: {feature.feature_name}"))
                    skipped_count += 1
                    continue

                # Preprocess feature_name to improve match (remove underscores, lowercase, etc.)
                cleaned_feature_name = feature.feature_name.lower().replace('_', ' ').replace('.', ' ').strip()

                best_match = None
                best_score = 0

                # Compare feature_name to each option_text using string similarity
                for option in options:
                    candidate_text = (option.option_text or '').lower().strip()
                    if not candidate_text:
                        continue

                    score = SequenceMatcher(None, cleaned_feature_name, candidate_text).ratio()

                    if score > best_score:
                        best_score = score
                        best_match = option

                # Set threshold to avoid bad matches (tweak as needed)
                if best_match and best_score > 0.85:
                    feature.encoded_option = best_match
                    feature.save()
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"✅ Matched: {feature.feature_name} → \"{best_match.option_text}\" (score={best_score:.2f})"
                    ))
                else:
                    skipped_count += 1
                    self.stdout.write(self.style.WARNING(
                        f"⚠️ Skipped (no good match): {feature.feature_name} (best_score={best_score:.2f})"
                    ))

            except Exception as e:
                skipped_count += 1
                self.stdout.write(self.style.ERROR(f"❌ Error on {feature.feature_name}: {e}"))

        # Final summary
        self.stdout.write("\n📊 Summary")
        self.stdout.write(self.style.SUCCESS(f"✅ Encoded options set: {updated_count}"))
        self.stdout.write(self.style.WARNING(f"⚠️ Skipped (unmatched or error): {skipped_count}"))
        self.stdout.write(self.style.NOTICE("🏁 Done.\n"))
