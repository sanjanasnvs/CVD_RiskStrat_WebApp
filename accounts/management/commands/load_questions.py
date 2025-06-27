import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import CVD_risk_Questionnaire

class Command(BaseCommand):
    help = 'Load questionnaire questions based on features used in the model input sample file.'

    def handle(self, *args, **kwargs):
        # ---------------------------------------
        # 📁 Define file paths
        # ---------------------------------------
        questions_file = os.path.join(settings.BASE_DIR, 'Questionnaire_data', 'TS_mapping_with_questions_v1.xlsx')
        dependencies_file = os.path.join(settings.BASE_DIR, 'Questionnaire_data', 'TS_advanced_mapping_v2 (1).xlsx')
        sample_file = os.path.join(settings.BASE_DIR, 'model_files', 'Input features sample files', 'biggestModelnoDropSample.csv')

        # ---------------------------------------
        # 📥 Step 1: Load feature list from model input CSV
        # ---------------------------------------
        try:
            sample_df = pd.read_csv(sample_file, header=None, skiprows=1)
            feature_names = sample_df[0].dropna().astype(str).str.strip()
        except Exception as e:
            self.stderr.write(f"❌ Could not read sample CSV: {e}")
            return

        # ✅ Only remove the prefix "category_{...}_ts_"
        def remove_prefix(name):
            if name.startswith("category_") and "_ts_" in name:
                return name.split("_ts_", 1)[1].strip()
            return name.strip()

        cleaned_features = [remove_prefix(name) for name in feature_names]

        # ---------------------------------------
        # 📥 Step 2: Load questions and categories from Excel
        # ---------------------------------------
        try:
            questions_df = pd.read_excel(questions_file)
            category_df = pd.read_excel(dependencies_file)
        except Exception as e:
            self.stderr.write(f"❌ Could not read Excel files: {e}")
            return

        # Clean column names
        questions_df.columns = questions_df.columns.str.strip()
        category_df.columns = category_df.columns.str.strip()

        # Drop rows with missing mappings
        filtered_questions_df = questions_df.dropna(subset=['Column names', 'Field ID']).copy()
        filtered_questions_df['Column names'] = filtered_questions_df['Column names'].astype(str).str.strip()
        filtered_questions_df['Field ID'] = filtered_questions_df['Field ID'].astype(int)

        # 🔗 Build mapping from column name to Field ID
        column_to_field = dict(zip(
            filtered_questions_df['Column names'],
            filtered_questions_df['Field ID']
        ))

        # Match cleaned features to Field IDs
        feature_field_ids = {column_to_field.get(f) for f in cleaned_features if f in column_to_field}
        feature_field_ids = {fid for fid in feature_field_ids if fid is not None}

        # ---------------------------------------
        # 🔄 Merge category info
        # ---------------------------------------
        merged_df = pd.merge(
            filtered_questions_df,
            category_df[['Field.ID', 'Category', 'Sub.category']],
            how='left',
            left_on='Field ID',
            right_on='Field.ID'
        )

        # Keep only rows that match features from the CSV
        valid_rows = merged_df[merged_df['Field ID'].isin(feature_field_ids)].drop_duplicates(subset=['Field ID'])

        print(f"✅ Prepared {len(valid_rows)} rows for insertion.\n")

        # ---------------------------------------
        # 💾 Load to DB
        # ---------------------------------------
        CVD_risk_Questionnaire.objects.all().delete()
        inserted = 0

        for order, (_, row) in enumerate(valid_rows.iterrows(), start=1):
            try:
                question_id = int(row['Field ID'])
                question_text = str(row.get('Question Stem', '')).strip()
                category = str(row.get('Category', '')).strip()
                subcategory = str(row['Sub.category']).strip() if pd.notna(row.get('Sub.category')) else None
                answer_type = str(row.get('Select one/Toggle multiple/Enter integer answer', '')).strip()

                if not all([question_id, question_text, category, answer_type]):
                    continue

                CVD_risk_Questionnaire.objects.create(
                    question_id=question_id,
                    question_text=question_text,
                    category=category,
                    subcategory=subcategory,
                    answer_type=answer_type,
                    question_order=order
                )
                print(f"✅ Inserted Q{question_id}: {question_text}")
                inserted += 1

            except Exception as e:
                print(f"❌ Skipped row due to error: {e}")

        print(f"\n🎯 Finished: {inserted} questions inserted into the database.\n")
