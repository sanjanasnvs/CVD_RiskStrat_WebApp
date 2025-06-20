# Generated by Django 5.2 on 2025-05-28 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_cvd_risk_questionnaire_answer_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="cvd_risk_responses",
            name="multi_selected_options",
            field=models.ManyToManyField(
                blank=True,
                related_name="multi_responses",
                to="accounts.cvd_risk_questionresponseoptions",
            ),
        ),
    ]
