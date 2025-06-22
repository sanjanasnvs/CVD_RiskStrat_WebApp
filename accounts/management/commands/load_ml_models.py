from django.core.management.base import BaseCommand
from accounts.models import ML_Models

class Command(BaseCommand):
    help = 'Load all ML models used for risk stratification.'

    def handle(self, *args, **kwargs):
        models = [
            {
                "model_name": "MRMR_COX_Sociodemographics",
                "model_type": "Cox PH Survival"
            },
            {
                "model_name": "MRMR_COX_Sociodemographics_Health_and_medical_history",
                "model_type": "Cox PH Survival"
            },
            {
                "model_name": "MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors",
                "model_type": "Cox PH Survival"
            },
            {
                "model_name": "MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors",
                "model_type": "Cox PH Survival"
            },
            {
                "model_name": "MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history",
                "model_type": "Cox PH Survival"
            },
            {
                "model_name": "MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history_Lifestyle_and_environment",
                "model_type": "Cox PH Survival"
            },
            {
                "model_name": "MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history_Lifestyle_and_environment_Psychosocial_factors",
                "model_type": "Cox PH Survival"
            }
                
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

