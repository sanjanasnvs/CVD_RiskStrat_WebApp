import joblib
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use('Agg')  # ✅ HEADLESS BACKEND to avoid macOS thread crash
import matplotlib.pyplot as plt

from survshap import PredictSurvSHAP
import os

def generate_explainability_plot(
    observation_row: pd.Series,
    full_feature_df: pd.DataFrame,
    model_name: str,
    patient_id: int,
    output_dir: str = "static/patient_plots"
):
    try:
        # Clean paths
        explainer_path = f"model_files/explainers/ktexplainer500{model_name}.pkl"
        model_path     = f"model_files/ML_models/ktmodel500{model_name}.pkl"

        # Load explainer and model
        explainer = joblib.load(explainer_path)
        model     = joblib.load(model_path)

        # Prepare input
        drop_cols = [
            'category_Sociodemographics_ts_Ethnic.background...Instance.0_3',
            'category_Sociodemographics_ts_Ethnic.background...Instance.0_4'
        ]
        df_cols = full_feature_df.drop(columns=drop_cols, errors="ignore").columns
        df      = pd.DataFrame([observation_row], columns=df_cols)

        df.rename(columns={'Age.at.recruitment': 'clinicalrisk_Age.at.recruitment'}, inplace=True)

        # Compute SHAP
        timestamps = list(range(16))
        survshap = PredictSurvSHAP(calculation_method="sampling", B=1, max_shap_value_inputs=10)
        survshap.fit(explainer=explainer, new_observation=df, timestamps=timestamps)
        shap_result = survshap.result

        # Prepare SHAP plot for top 10 variables
        time_cols = [f't = {t}' for t in timestamps]
        top_shap = shap_result.iloc[:10].set_index('variable_name')[time_cols]
        top_shap.columns = [int(col.replace('t = ', '')) for col in top_shap.columns]

        shap_df = top_shap.T  # time as index, vars as columns

        fig, ax = plt.subplots(figsize=(12, 6))
        for var in shap_df.columns:
            ax.plot(shap_df.index, shap_df[var], label=var, alpha=0.7)
            
        # Adjust title wrapping with line break if needed
        if len(model_name) > 40:
            # Add line break after first underscore
            parts = model_name.split('_', 1)
            if len(parts) == 2:
                model_title = parts[0] + '\n' + parts[1]
            else:
                model_title = model_name
        else:
            model_title = model_name

        fig.suptitle(f"Top 10 Feature SHAP Time-Series\n{model_title}", fontsize=14, wrap=True, ha='center')
        ax.set_xlabel("Time")
        ax.set_ylabel("SHAP Value")
        ax.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))

        # Make room for suptitle AND prevent clipping
        fig.tight_layout(rect=[0, 0, 1, 0.90])  # reserve more vertical space for the title

        os.makedirs(output_dir, exist_ok=True)
        plot_filename = f"patient_{patient_id}_explain_{model_name}.png"
        output_path = os.path.join(output_dir, plot_filename)
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)

        return f"patient_plots/{plot_filename}"

    except Exception as e:
        print(f"❌ Error generating explainability plot for {model_name}: {e}")
        return None
