# Generated by Django 5.2 on 2025-05-30 11:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_cvd_risk_responses_multi_selected_options"),
    ]

    operations = [
        migrations.CreateModel(
            name="CVD_risk_QuestionnaireDependency",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "trigger_values",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "from_question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="dependent_questions",
                        to="accounts.cvd_risk_questionnaire",
                    ),
                ),
                (
                    "to_question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="trigger_questions",
                        to="accounts.cvd_risk_questionnaire",
                    ),
                ),
            ],
            options={
                "verbose_name": "Question Dependency",
                "verbose_name_plural": "Question Dependencies",
                "db_table": "CVD_risk_Questionnaire_dependency_values",
                "unique_together": {("from_question", "to_question")},
            },
        ),
    ]
