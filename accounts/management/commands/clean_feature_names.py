from django.core.management.base import BaseCommand
from accounts.models import CVD_Risk_Model_InputFeatures

class Command(BaseCommand):
    help = "Clean and normalize feature_name in CVD_Risk_Model_InputFeatures by stripping category prefixes."

    def handle(self, *args, **kwargs):
        # Common prefixes used during Excel upload
        known_prefixes = [
            "category_Sociodemographics_ts_",
            "category_Health and medical history_ts_",
            "category_Sex-specific factors_ts_",
            "category_Early life factors_ts_",
            "category_Family history_ts_",
            "category_Lifestyle and environment_ts_",
            "category_Psychosocial factors_ts_",
        ]

        updated = 0
        skipped = 0

        for feature in CVD_Risk_Model_InputFeatures.objects.all():
            original = feature.feature_name
            cleaned = original

            for prefix in known_prefixes:
                if original.startswith(prefix):
                    cleaned = original[len(prefix):]
                    break  # Stop after matching first prefix

            if cleaned != original:
                feature.feature_name = cleaned
                feature.save()
                self.stdout.write(self.style.SUCCESS(f"✔ Updated: {original} → {cleaned}"))
                updated += 1
            else:
                skipped += 1

        self.stdout.write(self.style.NOTICE("\n🧹 Cleaning complete"))
        self.stdout.write(f"✅ Updated: {updated}")
        self.stdout.write(f"⏭️ Skipped (already clean): {skipped}")

