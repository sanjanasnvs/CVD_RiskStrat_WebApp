import pandas as pd
import os
import re
from django.utils import timezone
from accounts.models import (
    CVD_Risk_Model_InputFeatures,
    CVD_risk_Responses,
    CVD_ModelFeatureMappings,
    CVD_Risk_FeatureThresholds,
    CVD_Risk_CalculatedFeatures,
    FeatureOptionMapping,
    ML_Models,
)

def calculate_features(patient_id, submission_id):
    """
    Calculates model input features for a patient based on their responses.
    Supports:
    - Categorical features (single- and multi-select)
    - Numeric features binned into tertiles (only one active at a time)
    """

    # 1. Load feature order from Excel template
    template_path = 'model_files/feature_templates/model1_sociodemographic_features.xlsx'
    try:
        feature_order = pd.read_excel(template_path, header=None)[0].tolist()
    except Exception as e:
        print(f"❌ Error loading feature template: {e}")
        return

    # 2. Load ML model metadata
    try:
        model = ML_Models.objects.get(model_name='MRMR_COX_Sociodemographics')
    except ML_Models.DoesNotExist:
        print("❌ Model not found in DB.")
        return

    # 3. Map feature names from DB for quick lookup
    mappings = CVD_ModelFeatureMappings.objects.filter(model=model).select_related('input_feature')
    model_features = {m.input_feature.feature_name: m.input_feature for m in mappings}

    # 4. Initialize feature vector to all zeros
    feature_values = {fname: 0 for fname in feature_order}

    # 5. Group tertile features by their base (e.g., "X" for "X_Lower.third")
    tertile_groups = {}
    for fname in feature_order:
        clean_name = re.sub(r'^category_\w+_ts_', '', fname).strip()
        if any(suffix in clean_name for suffix in ['_Lower.third', '_Middle.third', '_Upper.third']):
            base = clean_name.rsplit('_', 1)[0]
            tertile_groups.setdefault(base, []).append((fname, clean_name))

    # 6. Process each feature
    for fname in feature_order:
        full_feature_name = re.sub(r'^category_\w+_ts_', '', fname).strip()

        if full_feature_name not in model_features:
            print(f"⚠️ Input feature not found in DB: {full_feature_name}")
            continue

        feature_obj = model_features[full_feature_name]
        question = feature_obj.question

        try:
            response = CVD_risk_Responses.objects.filter(
                patient_id=patient_id,
                question=question
            ).order_by('-last_updated').first()

            if not response:
                print(f"⚠️ No response found for question: {question}")
                continue

            # === Case A: Numeric (Tertile) ===
            if response.response_type == 'Enter integer answer' and response.numeric_response is not None:
                val = response.numeric_response
                base_name = full_feature_name.rsplit('_', 1)[0]

                if base_name in tertile_groups:
                    triplet = tertile_groups[base_name]

                    # Step 1: Fetch available thresholds
                    thresholds_by_suffix = {}
                    expected_tertile_suffixes = []
                    for col_name, clean_name in triplet:
                        feat_obj = model_features.get(clean_name)
                        if not feat_obj:
                            continue
                        if 'Lower.third' in clean_name:
                            expected_tertile_suffixes.append('Lower.third')
                        elif 'Middle.third' in clean_name:
                            expected_tertile_suffixes.append('Middle.third')
                        elif 'Upper.third' in clean_name:
                            expected_tertile_suffixes.append('Upper.third')

                        threshold = (
                            CVD_Risk_FeatureThresholds.objects
                            .filter(feature=feat_obj)
                            .values_list('threshold_value', flat=True)
                            .first()
                        )

                        if threshold is not None:
                            if 'Lower.third' in clean_name:
                                thresholds_by_suffix['Lower.third'] = (col_name, threshold)
                            elif 'Middle.third' in clean_name:
                                thresholds_by_suffix['Middle.third'] = (col_name, threshold)
                            elif 'Upper.third' in clean_name:
                                thresholds_by_suffix['Upper.third'] = (col_name, threshold)

                    # Step 2: Try to infer missing thresholds
                    suffixes = thresholds_by_suffix.keys()
                    try:
                        if 'Lower.third' in suffixes and 'Upper.third' in suffixes and 'Middle.third' not in suffixes:
                            lower_val = thresholds_by_suffix['Lower.third'][1]
                            upper_val = thresholds_by_suffix['Upper.third'][1]
                            middle_val = (lower_val + upper_val) / 2
                            # 🔧 FIX: Get Middle.third column name from feature_order
                            middle_col = next(
                                (f for f in feature_order if re.sub(r'^category_\w+_ts_', '', f).strip().endswith('_Middle.third') and base_name in f),
                                None
                            )
                            if middle_col:
                                thresholds_by_suffix['Middle.third'] = (middle_col, middle_val)
                        elif 'Lower.third' in suffixes and 'Middle.third' in suffixes and 'Upper.third' not in suffixes:
                            lower_val = thresholds_by_suffix['Lower.third'][1]
                            middle_val = thresholds_by_suffix['Middle.third'][1]
                            upper_val = 2 * middle_val - lower_val
                            upper_col = next(
                                (f for f in feature_order if re.sub(r'^category_\w+_ts_', '', f).strip().endswith('_Upper.third') and base_name in f),
                                None
                            )
                            if upper_col:
                                thresholds_by_suffix['Upper.third'] = (upper_col, upper_val)
                        elif 'Middle.third' in suffixes and 'Upper.third' in suffixes and 'Lower.third' not in suffixes:
                            upper_val = thresholds_by_suffix['Upper.third'][1]
                            middle_val = thresholds_by_suffix['Middle.third'][1]
                            lower_val = 2 * middle_val - upper_val
                            lower_col = next(
                                (f for f in feature_order if re.sub(r'^category_\w+_ts_', '', f).strip().endswith('_Lower.third') and base_name in f),
                                None
                            )
                            if lower_col:
                                thresholds_by_suffix['Lower.third'] = (lower_col, lower_val)
                    except Exception as e:
                        print(f"❌ Error inferring tertile thresholds for base {base_name}: {e}")

                    # Step 3: Validate if all *required* thresholds are available
                    missing_suffixes = []
                    for required in expected_tertile_suffixes:
                        if required not in thresholds_by_suffix:
                            missing_suffixes.append(required)

                    if missing_suffixes:
                        print(f"⚠️ Missing thresholds for base: {base_name} → {', '.join(missing_suffixes)}")
                        continue

                    # Step 4: Apply one-hot logic
                    lower_col, lower_val = thresholds_by_suffix.get('Lower.third', (None, float('-inf')))
                    middle_col, middle_val = thresholds_by_suffix.get('Middle.third', (None, float('inf')))
                    upper_col, upper_val = thresholds_by_suffix.get('Upper.third', (None, float('inf')))

                    if 'Lower.third' in thresholds_by_suffix and val <= lower_val:
                        feature_values[lower_col] = 1
                    elif 'Middle.third' in thresholds_by_suffix and val <= middle_val:
                        feature_values[middle_col] = 1
                    elif 'Upper.third' in thresholds_by_suffix:
                        feature_values[upper_col] = 1

                else:
                    # Case: Raw numeric feature (not binned)
                    feature_values[fname] = float(val)

            # === Case B: Single-select categorical ===
            elif response.response_type == 'Select one answer':
                try:
                    mapping = FeatureOptionMapping.objects.get(feature_name=full_feature_name)
                    if response.option_selected and response.option_selected.id == mapping.option.id:
                        feature_values[fname] = 1
                except FeatureOptionMapping.DoesNotExist:
                    print(f"⚠️ No mapping found for feature: {full_feature_name}")
                except Exception as e:
                    print(f"❌ Error in single-select: {e}")

            # === Case C: Multi-select categorical ===
            elif response.response_type == 'Toggle multiple answer':
                try:
                    mapping = FeatureOptionMapping.objects.get(feature_name=full_feature_name)
                    selected_ids = [opt.id for opt in response.multi_selected_options.all()]
                    if mapping.option.id in selected_ids:
                        feature_values[fname] = 1
                except FeatureOptionMapping.DoesNotExist:
                    print(f"⚠️ No mapping found for feature: {full_feature_name}")
                except Exception as e:
                    print(f"❌ Error in multi-select: {e}")

        except Exception as e:
            print(f"❌ Error processing feature {full_feature_name}: {e}")
            continue

    # 7. Save results to DB
    saved_count = 0
    timestamp = timezone.now()

    for fname, value in feature_values.items():
        full_feature_name = re.sub(r'^category_\w+_ts_', '', fname).strip()
        try:
            feature_obj = model_features[full_feature_name]
            CVD_Risk_CalculatedFeatures.objects.update_or_create(
                patient_id=patient_id,
                model=model,
                feature=feature_obj,
                defaults={'value': value, 'created_at': timestamp}
            )
            saved_count += 1
        except Exception as e:
            print(f"❌ Error saving feature {full_feature_name}: {e}")

    print(f"✅ Saved or updated {saved_count} features for patient {patient_id}")

    # 8. Export model input to CSV
    try:
        df_out = pd.DataFrame([feature_values])
        os.makedirs("model_outputs", exist_ok=True)
        out_path = f"model_outputs/patient_{patient_id}_model1_input.csv"
        df_out.to_csv(out_path, index=False)
        print(f"📁 CSV saved to: {out_path}")
    except Exception as e:
        print(f"❌ Failed to save CSV: {e}")

    return feature_values
