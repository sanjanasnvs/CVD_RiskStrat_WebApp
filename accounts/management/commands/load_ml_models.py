from django.core.management.base import BaseCommand
from accounts.models import ML_Models

class Command(BaseCommand):
    help = 'Load initial ML models used for risk stratification.'

    def handle(self, *args, **kwargs):
        models = [
            {
                "model_name": "MRMR_COX_Sociodemographics",
                "model_type": "Cox PH Survival"
            },
            # Add more models here later as needed
        ]

        for entry in models:
            obj, created = ML_Models.objects.get_or_create(
                model_name=entry["model_name"],
                defaults={"model_type": entry["model_type"]}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Added model: {obj.model_name}"))
            else:
                self.stdout.write(f"ℹ️ Model already exists: {obj.model_name}")

