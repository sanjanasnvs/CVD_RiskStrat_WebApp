import pandas as pd
import numpy as np
import re

def calculate_features_from_responses(response_dict,
                                      ts_mapping_file="Questionnaire_data/TS_mapping_with_questions_v1.xlsx",
                                      tertile_file="Questionnaire_data/Thirds_threshold_values.xlsx",
                                      category_mapping_file="Questionnaire_data/TS_advanced_mapping_v2 (1).xlsx"):
    """
    Converts patient responses into model-aligned features based on selected answers and numeric thresholds.

    Parameters:
    - response_dict: Dictionary of normalized_question_text: value(s)
    - Returns: Dictionary of aligned features (1 or 0 encoded)
    """

    import pandas as pd
    import re

    def normalize(text):
        return str(text).strip().replace('\n', ' ').replace('\r', '').lower()

    print("📥 Incoming user responses:")
    for q, a in response_dict.items():
        print(f"  {q}: {a}")

    # -----------------------------
    # STEP 1: Load TS mapping file
    # -----------------------------
    ts_df = pd.read_excel(ts_mapping_file).dropna(subset=[
        "Field ID", "Question Stem", "Column names", "Select one/Toggle multiple/Enter integer answer"
    ]).copy()

    # Extract code from "Full Answer" column (e.g., '1 : Some answer' → 1)
    ts_df["value_range_start"] = ts_df["Full Answer"].map(lambda x: int(re.match(r"^\s*(-?\d+)", str(x)).group(1)) if re.match(r"^\s*(-?\d+)", str(x)) else None)
    ts_df["question_text_norm"] = ts_df["Question Stem"].map(normalize)
    ts_df["response_type"] = ts_df["Select one/Toggle multiple/Enter integer answer"].str.strip().str.lower()
    ts_df["feature"] = ts_df["Column names"].str.strip()

    # -----------------------------
    # STEP 2: Load Category Mapping
    # -----------------------------
    category_df = pd.read_excel(category_mapping_file)
    category_df["feature"] = category_df["Column.names"].str.strip()
    ts_df = pd.merge(ts_df, category_df[["feature", "Category"]], on="feature", how="left")

    # -----------------------------
    # STEP 3: Load tertile thresholds
    # -----------------------------
    tertile_df = pd.read_excel(tertile_file).dropna(subset=["columnName", "threshold"])

    def extract_base_and_type(col_name):
        norm = str(col_name).lower()
        if "lower.third" in norm:
            return col_name.split("_")[0], "Lower third"
        elif "upper.third" in norm:
            return col_name.split("_")[0], "Upper third"
        elif "middle.third" in norm:
            return col_name.split("_")[0], "Middle third"
        return None, None

    tertile_df[["feature_base", "tertile_type"]] = tertile_df["columnName"].apply(lambda x: pd.Series(extract_base_and_type(x)))
    tertile_df = tertile_df.dropna()
    threshold_dict = tertile_df.pivot(index="feature_base", columns="tertile_type", values="threshold").to_dict(orient="index")

    # -----------------------------
    # STEP 4: Process responses
    # -----------------------------
    features = {}

    for q_norm, user_value in response_dict.items():
        matching_rows = ts_df[ts_df["question_text_norm"] == q_norm]

        if matching_rows.empty:
            print(f"⚠️ No mapping found for: {q_norm}")
            continue

        response_type = matching_rows["response_type"].iloc[0]
        category = matching_rows["Category"].iloc[0]
        print(f"\n🔍 Q: {q_norm} → type: {response_type} → user answer: {user_value}")

        # -----------------------------
        # Case A: Numeric input
        # -----------------------------
        if response_type == "enter integer answer":
            try:
                val = float(user_value)
                base_feature = matching_rows["feature"].iloc[0].split("_")[0]
                thresholds = threshold_dict.get(base_feature, {})

                for tertile in ["Lower third", "Middle third", "Upper third"]:
                    suffix = tertile.replace(" ", ".")
                    full_feature = f"category_{category.replace(' ', '')}_ts_{base_feature}_{suffix}"

                    if tertile == "Lower third":
                        result = int(val < thresholds.get("Lower third", float("-inf")))
                    elif tertile == "Upper third":
                        result = int(val > thresholds.get("Upper third", float("inf")))
                    else:
                        result = int(thresholds.get("Lower third", float("-inf")) <= val <= thresholds.get("Upper third", float("inf")))

                    features[full_feature] = result
                    print(f"  ✅ {full_feature} = {result}")
            except Exception as e:
                print(f"  ⚠️ Error processing numeric: {e}")

        # -----------------------------
        # Case B: Single-select
        # -----------------------------
        elif response_type == "select one answer":
            try:
                selected_val = int(float(user_value))
                for _, row in matching_rows.iterrows():
                    feature_key = f"category_{row['Category'].replace(' ', '')}_ts_{row['feature']}"
                    is_selected = int(row["value_range_start"] == selected_val)
                    features[feature_key] = is_selected
                    print(f"  ✅ {feature_key} = {is_selected}")
            except Exception as e:
                print(f"  ⚠️ Error processing single-select: {e}")

        # -----------------------------
        # Case C: Multi-select
        # -----------------------------
        elif response_type == "toggle multiple answer":
            try:
                selected_values = [int(v) for v in (user_value if isinstance(user_value, list) else [user_value])]
                for _, row in matching_rows.iterrows():
                    feature_key = f"category_{row['Category'].replace(' ', '')}_ts_{row['feature']}"
                    is_selected = int(row["value_range_start"] in selected_values)
                    features[feature_key] = is_selected
                    print(f"  ✅ {feature_key} = {is_selected}")
            except Exception as e:
                print(f"  ⚠️ Error processing multi-select: {e}")

    print(f"\n✅ Final features generated: {len(features)}")
    return features


def should_display_question(question, saved_responses):
    """
    Determines whether a question should be displayed based on its dependencies.
    """
    dependencies = question.trigger_questions.all()

    for dep in dependencies:
        trigger_q = dep.triggering_question
        trigger_value = saved_responses.get(trigger_q.question_id)

        if trigger_value is None:
            return False

        if dep.trigger_values and int(trigger_value) not in dep.trigger_values:
            return False

    return True  # No unmet dependencies

