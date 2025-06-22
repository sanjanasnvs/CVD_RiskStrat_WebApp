from django.core.management.base import BaseCommand
from accounts.models import ML_Models, CVD_ModelFeatureMappings, CVD_Risk_Model_InputFeatures
import pandas as pd

class Command(BaseCommand):
    help = "Maps model1 features (Sociodemographics) to the MRMR_COX_Sociodemographics model in the CVD_ModelFeatureMappings table."

    def handle(self, *args, **kwargs):
        try:
            # Load model
            model_name = 'MRMR_COX_Sociodemographics'
            model = ML_Models.objects.get(model_name=model_name)
            self.stdout.write(self.style.SUCCESS(f"✅ Loaded model: {model_name}"))

            # Load feature names from Excel
            path = 'model_files/feature_templates/model1_sociodemographic_features.xlsx'
            features = pd.read_excel(path, header=None)[0].tolist()
            self.stdout.write(self.style.SUCCESS(f"📄 Loaded {len(features)} feature names from Excel"))

            count = 0
            for fname in features:
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
            self.stdout.write(self.style.ERROR(f"❌ Model {model_name} not found in ML_Models table"))

