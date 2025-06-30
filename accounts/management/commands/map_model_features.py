from django.core.management.base import BaseCommand
from accounts.models import ML_Models, CVD_ModelFeatureMappings, CVD_Risk_Model_InputFeatures
import pandas as pd
import re
import os


class Command(BaseCommand):
    help = "Maps features from an Excel file to a given model by stripping category prefixes."

    def add_arguments(self, parser):
        parser.add_argument('model_name', type=str, help="Model name in ML_Models table")
        parser.add_argument('template_file', type=str, help="Path to Excel file with feature list")

    def handle(self, *args, **kwargs):
        model_name = kwargs['model_name']
        template_file = kwargs['template_file']
        file_ext = os.path.splitext(template_file)[1].lower()

        try:
            model = ML_Models.objects.get(model_name=model_name)
            self.stdout.write(self.style.SUCCESS(f"✅ Loaded model: {model_name}"))
        except ML_Models.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ Model not found: {model_name}"))
            return

        try:
            if file_ext == ".csv":
                features = pd.read_csv(template_file, header=None)[0].tolist()
            elif file_ext in [".xlsx", ".xls"]:
                features = pd.read_excel(template_file, header=None)[0].tolist()
            else:
                self.stdout.write(self.style.ERROR(f"❌ Unsupported file format: {file_ext}"))
                return

            self.stdout.write(self.style.SUCCESS(f"📄 Loaded {len(features)} features from file: {template_file}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to read file: {e}"))
            return


        count = 0
        missing = 0
        for raw_feature in features:
            # Strip category prefix and 'ts' if present
            clean_feature = re.sub(r'^category_.*?_ts_', '', str(raw_feature)).strip()
            print(f"🧹 Raw: {raw_feature} ➜ Cleaned: {clean_feature}")


            try:
                feat_obj = CVD_Risk_Model_InputFeatures.objects.get(feature_name=clean_feature)
                _, created = CVD_ModelFeatureMappings.objects.get_or_create(
                    model=model,
                    input_feature=feat_obj
                )
                count += 1
            except CVD_Risk_Model_InputFeatures.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"⚠️ Feature not found in DB: {clean_feature}"))
                missing += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error mapping {clean_feature}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"✅ Successfully mapped {count} features"))
        if missing:
            self.stdout.write(self.style.WARNING(f"⚠️ {missing} features were not found in DB"))

