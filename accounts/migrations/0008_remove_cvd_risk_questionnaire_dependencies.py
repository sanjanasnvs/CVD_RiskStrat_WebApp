# Generated by Django 5.2 on 2025-05-30 12:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0007_cvd_risk_questionnairedependency"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="cvd_risk_questionnaire",
            name="dependencies",
        ),
    ]
