from django.core.management.base import BaseCommand
from accounts.models import ML_Models, CVD_ModelFeatureMappings, CVD_Risk_Model_InputFeatures
import pandas as pd

class Command(BaseCommand):
    help = "Maps features to MRMR_COX_Sociodemographics_Health_and_medical_history model."

    def handle(self, *args, **kwargs):
        try:
            model_name = 'MRMR_COX_Sociodemographics_Health_and_medical_history'
            model = ML_Models.objects.get(model_name=model_name)
            self.stdout.write(self.style.SUCCESS(f"✅ Loaded model: {model_name}"))

            # Combine features from category 1 and 2
            files = [
                'model_files/feature_templates/model1_sociodemographic_features.xlsx',
                'model_files/feature_templates/model2_healthandmed_features.xlsx'
            ]
            all_features = []
            for path in files:
                try:
                    features = pd.read_excel(path, header=None)[0].tolist()
                    all_features.extend(features)
                    self.stdout.write(self.style.SUCCESS(f"📄 Loaded {len(features)} features from {path}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Error reading {path}: {e}"))

            count = 0
            for fname in all_features:
                try:
                    feat = CVD_Risk_Model_InputFeatures.objects.get(feature_name=fname)
                    _, created = CVD_ModelFeatureMappings.objects.get_or_create(
                        model=model,
                        input_feature=feat
                    )
                    count += 1
                except CVD_Risk_Model_InputFeatures.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"⚠️ Feature not found in DB: {fname}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Error mapping {fname}: {e}"))

            self.stdout.write(self.style.SUCCESS(f"✅ Mapped {count} features to model: {model_name}"))

        except ML_Models.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ Model {model_name} not found"))
