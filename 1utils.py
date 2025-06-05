
import pandas as pd
import numpy as np

def calculate_features_from_responses(response_dict):
    mapping_df = pd.read_excel("Questionnaire_data/TS_mapping_with_questions_v1.xlsx")
    thresholds_df = pd.read_csv("Questionnaire_data/Thirds_threshold_values.tsv", sep="\t")

    features = {}

    for _, row in mapping_df.iterrows():
        feature_name = row['Column names']
        question_col = row['Column names'].split('...')[0]
        raw_value = response_dict.get(question_col, None)

        if raw_value is None:
            features[feature_name] = 0
            continue

        # Tertile logic
        if any(x in feature_name for x in ["Lower.third", "Upper.third", "Middle.third"]):
            try:
                lower = float(thresholds_df[thresholds_df['threshold'] == feature_name.replace("Middle.third", "Lower.third")]['Threshold'].values[0])
                upper = float(thresholds_df[thresholds_df['threshold'] == feature_name.replace("Middle.third", "Upper.third")]['Threshold'].values[0])
                val = float(raw_value)
            except:
                features[feature_name] = 0
                continue

            if "Lower.third" in feature_name:
                features[feature_name] = 1 if val <= lower else 0
            elif "Upper.third" in feature_name:
                features[feature_name] = 1 if val >= upper else 0
            elif "Middle.third" in feature_name:
                features[feature_name] = 1 if lower < val < upper else 0
        else:
            # Categorical/binary features
            selected_option = str(raw_value).strip().lower()
            feature_id = row['Column names'].strip().lower()
            features[feature_name] = 1 if feature_id == selected_option else 0

    return features

