import matplotlib
matplotlib.use('Agg')
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import joblib
from survshap import PredictSurvSHAP

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


def generate_survshap_plots(
    observation: np.ndarray,
    sampleDFsocioCols: pd.DataFrame,
    explainer_path: str,
    model_path: str,
    timestamps: list = None,
    B: int = 1,
    max_shap_vars: int = 10,
    n_vars_plot: int = 10
):
    explainer = joblib.load(explainer_path)
    model     = joblib.load(model_path)
    if hasattr(explainer, 'y') and isinstance(explainer.y, pd.DataFrame):
        explainer.y = explainer.y.to_records(index=False)

    # Always use explainer.data.columns for alignment
    df_cols = explainer.data.columns
    df      = pd.DataFrame([observation], columns=df_cols)

    df = df.rename(columns={'Age.at.recruitment': 'clinicalrisk_Age.at.recruitment'})

    if timestamps is None:
        timestamps = list(range(16))
    survshap = PredictSurvSHAP(
        calculation_method="sampling",
        B=B,
        max_shap_value_inputs=max_shap_vars
    )
    survshap.fit(
        explainer=explainer,
        new_observation=df,
        timestamps=timestamps
    )
    shap_result = survshap.result

    def _plot(fig_size=(8,5)):
        times = np.array(timestamps)

        # (a) cohort average risk
        model = explainer.model
        surv_cohort = model.predict_survival_function(
            explainer.data, return_array=True
        )[:, :len(times)].mean(axis=0)
        risk_cohort = 1 - surv_cohort
        df.columns = explainer.data.columns
        # (b) individual risk
        surv_ind = model.predict_survival_function(
            df, return_array=True
        )[0, :len(times)]
        risk_ind = 1 - surv_ind

        fig1, ax1 = plt.subplots(figsize=fig_size)
        ax1.plot(times, risk_cohort, 'k--', lw=2, label='Cohort avg. risk')
        ax1.plot(times, risk_ind,    'r-',  lw=2, label='Individual risk')
        ax1.set(
            xlabel='Timepoint',
            ylabel='Risk (1 – Survival)',
            title='Cohort vs. Individual Risk over Time'
        )
        ax1.legend()
        fig1.tight_layout()

        time_cols = [f't = {t}' for t in times]
        top_shap  = shap_result.iloc[:n_vars_plot].set_index('variable_name')
        shap_df   = top_shap[time_cols].T
        shap_df.index = shap_df.index.str.replace('t = ', '').astype(int)

        fig2, ax2 = plt.subplots(figsize=(15,6))
        for var in shap_df.columns:
            ax2.plot(shap_df.index, shap_df[var], alpha=0.7, label=var)
        ax2.set(
            xlabel='Timepoint',
            ylabel='SHAP value',
            title=f'Top {n_vars_plot} Variables over {len(times)} Time‐steps'
        )
        ax2.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
        fig2.tight_layout()

        return fig1, fig2

    # --- 5) Generate and return both figures ---
    return _plot()

