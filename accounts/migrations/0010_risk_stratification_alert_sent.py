# Generated by Django 5.2 on 2025-06-04 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "accounts",
            "0009_rename_to_question_cvd_risk_questionnairedependency_conditional_question_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="risk_stratification",
            name="alert_sent",
            field=models.BooleanField(default=False),
        ),
    ]
