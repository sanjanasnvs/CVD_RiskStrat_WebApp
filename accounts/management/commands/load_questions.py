import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import CVD_risk_Questionnaire

class Command(BaseCommand):
    help = 'Load questionnaire questions into the database, filtering Sociodemographics based on a sample dataset.'

    def handle(self, *args, **kwargs):
        # Define file paths
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(settings.BASE_DIR, 'Questionnaire_data')
        questions_file = os.path.join(data_dir, 'TS_mapping_with_questions_v1.xlsx')
        dependencies_file = os.path.join(data_dir, 'TS_advanced_mapping_v2 (1).xlsx')
        sample_file = os.path.join(settings.BASE_DIR, 'model_files', 'sociodemographicsSample (1).csv')

        print("📄 Loading full questionnaire Excel file...")
        questions_df = pd.read_excel(questions_file)
        questions_df.columns = questions_df.columns.str.strip()

        print("📄 Loading category mapping file...")
        category_df = pd.read_excel(dependencies_file)
        category_df.columns = category_df.columns.str.strip()

        print("📄 Loading sample dataset for Sociodemographics...")
        sample_df = pd.read_csv(sample_file, header=None)
        sample_columns = sample_df[0].dropna().str.strip()

        # Handle feature names with and without prefix
        prefix = 'category_Sociodemographics_ts_'
        sociodemographic_features = []

        for feature in sample_columns:
            if feature.startswith(prefix):
                cleaned_feature = feature.replace(prefix, '', 1)
                sociodemographic_features.append(cleaned_feature)
            else:
                # Directly add feature without prefix
                sociodemographic_features.append(feature)

        # Map feature names to Field IDs
        column_to_field = dict(zip(questions_df['Column names'], questions_df['Field ID']))
        sociodemographic_field_ids = set()
        for feature in sociodemographic_features:
            field_id = column_to_field.get(feature)
            if pd.notna(field_id):
                sociodemographic_field_ids.add(int(field_id))

        print("🔁 Merging category & subcategory info into main question file...")
        merged_df = pd.merge(
            questions_df,
            category_df[['Field.ID', 'Category', 'Sub.category']],
            how='left',
            left_on='Field ID',
            right_on='Field.ID'
        )

        print("🔍 Filtering relevant questions...")
        seen_ids = set()
        valid_rows = []

        for _, row in merged_df.iterrows():
            field_id = row.get('Field ID')
            category = row.get('Category')
            if pd.isna(field_id) or pd.isna(category):
                continue

            if field_id in seen_ids:
                continue

            if category == 'Sociodemographics':
                if int(field_id) in sociodemographic_field_ids:
                    valid_rows.append(row)
                    seen_ids.add(field_id)
            else:
                valid_rows.append(row)
                seen_ids.add(field_id)

        print(f"✅ Loaded {len(valid_rows)} valid questions after filtering.\n")

        # Clear existing DB entries
        print("🧹 Clearing existing questionnaire entries...")
        CVD_risk_Questionnaire.objects.all().delete()

        print("💾 Inserting questions into database...\n")
        imported = 0
        for order, row in enumerate(valid_rows, start=1):
            try:
                question_id = int(row.get('Field ID'))
                question_text = row.get('Question Stem', '').strip()
                category = row.get('Category', '').strip()
                subcategory = row.get('Sub.category', '').strip() if pd.notna(row.get('Sub.category')) else None
                answer_type = row.get('Select one/Toggle multiple/Enter integer answer', '').strip()

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
                imported += 1
            except Exception as e:
                print(f"⚠️ Skipped row due to error: {e}")

        print(f"✅ Successfully inserted {imported} questions.\n")
