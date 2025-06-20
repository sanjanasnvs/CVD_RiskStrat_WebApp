# Generated by Django 5.2 on 2025-05-10 11:03

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="batch_CVD_Risk_Features",
            fields=[
                ("feature_id", models.AutoField(primary_key=True, serialize=False)),
                ("feature_name", models.CharField(max_length=255)),
                ("feature_description", models.TextField(blank=True, null=True)),
            ],
            options={
                "verbose_name_plural": "Batch CVD Risk Features",
                "db_table": "batch_CVD_Risk_Features",
            },
        ),
        migrations.CreateModel(
            name="batch_CVD_Risk_Risk",
            fields=[
                ("risk_id", models.AutoField(primary_key=True, serialize=False)),
                ("risk_score", models.DecimalField(decimal_places=2, max_digits=5)),
                ("prediction_date", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name_plural": "Batch CVD Risk Risk",
                "db_table": "batch_CVD_Risk_Risk",
            },
        ),
        migrations.CreateModel(
            name="ML_Models",
            fields=[
                ("model_id", models.AutoField(primary_key=True, serialize=False)),
                ("model_name", models.CharField(max_length=255)),
                ("model_type", models.CharField(max_length=100)),
            ],
            options={
                "verbose_name_plural": "ML Models",
                "db_table": "ML_Models",
            },
        ),
        migrations.CreateModel(
            name="Users",
            fields=[
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                ("user_id", models.AutoField(primary_key=True, serialize=False)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("first_name", models.CharField(max_length=50)),
                ("last_name", models.CharField(max_length=50)),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("patient", "Patient"),
                            ("clinician_pending", "Clinician Pending"),
                            ("clinician_approved", "Clinician Approved"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Users",
                "db_table": "Users",
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="batch_CVD_Risk_Output",
            fields=[
                ("output_id", models.AutoField(primary_key=True, serialize=False)),
                ("plot_type", models.CharField(max_length=100)),
                ("generated_at", models.DateTimeField(auto_now_add=True)),
                (
                    "risk",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.batch_cvd_risk_risk",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Batch CVD Risk Output",
                "db_table": "batch_CVD_Risk_Output",
            },
        ),
        migrations.CreateModel(
            name="Clinicians",
            fields=[
                ("clinician_id", models.AutoField(primary_key=True, serialize=False)),
                ("specialty", models.CharField(blank=True, max_length=100, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Clinicians",
                "db_table": "Clinicians",
            },
        ),
        migrations.CreateModel(
            name="CVD_risk_Questionnaire",
            fields=[
                ("question_id", models.AutoField(primary_key=True, serialize=False)),
                ("question_text", models.TextField()),
                ("category", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "subcategory",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("question_order", models.IntegerField(default=0)),
                (
                    "dependencies",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="accounts.cvd_risk_questionnaire",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "CVD Risk Questionnaire",
                "db_table": "CVD_risk_Questionnaire",
            },
        ),
        migrations.CreateModel(
            name="CVD_risk_QuestionResponseOptions",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("option_text", models.TextField()),
                ("value_range_start", models.FloatField(blank=True, null=True)),
                ("value_range_end", models.FloatField(blank=True, null=True)),
                (
                    "option_label",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.cvd_risk_questionnaire",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Questionnaire Response Options",
                "db_table": "CVD_risk_QuestionResponseOptions",
            },
        ),
        migrations.AddField(
            model_name="batch_cvd_risk_risk",
            name="model",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="accounts.ml_models"
            ),
        ),
        migrations.CreateModel(
            name="Patients",
            fields=[
                ("patient_id", models.AutoField(primary_key=True, serialize=False)),
                ("date_of_birth", models.DateField(blank=True, null=True)),
                (
                    "gender",
                    models.CharField(
                        choices=[
                            ("Male", "Male"),
                            ("Female", "Female"),
                            ("Other", "Other"),
                        ],
                        max_length=10,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Patients",
                "db_table": "Patients",
            },
        ),
        migrations.CreateModel(
            name="CVD_risk_Responses",
            fields=[
                ("response_id", models.AutoField(primary_key=True, serialize=False)),
                ("response_type", models.CharField(max_length=50)),
                ("numeric_response", models.FloatField(blank=True, null=True)),
                ("boolean_response", models.BooleanField(blank=True, null=True)),
                ("response_date", models.DateTimeField(auto_now_add=True)),
                (
                    "option_selected",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="accounts.cvd_risk_questionresponseoptions",
                    ),
                ),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.cvd_risk_questionnaire",
                    ),
                ),
                (
                    "patient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.patients",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "CVD Risk Responses",
                "db_table": "CVD_risk_Responses",
            },
        ),
        migrations.CreateModel(
            name="CVD_risk_Patient_Outcomes",
            fields=[
                ("outcome_id", models.AutoField(primary_key=True, serialize=False)),
                ("outcome_description", models.TextField()),
                ("reported_at", models.DateTimeField(auto_now_add=True)),
                (
                    "patient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.patients",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "CVD Risk Patient Outcomes",
                "db_table": "CVD_risk_Patient_Outcomes",
            },
        ),
        migrations.AddField(
            model_name="batch_cvd_risk_risk",
            name="patient",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="accounts.patients"
            ),
        ),
        migrations.CreateModel(
            name="Risk_Stratification",
            fields=[
                (
                    "stratification_id",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                ("risk_score", models.DecimalField(decimal_places=2, max_digits=5)),
                ("recommendation", models.TextField()),
                ("assessed_at", models.DateTimeField(auto_now_add=True)),
                (
                    "model",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="accounts.ml_models",
                    ),
                ),
                (
                    "patient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.patients",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Risk Stratification",
                "db_table": "Risk_Stratification",
            },
        ),
        migrations.CreateModel(
            name="batch_CVD_Risk_Model_Features",
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
                    "feature",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.batch_cvd_risk_features",
                    ),
                ),
                (
                    "model",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.ml_models",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Batch CVD Risk Model Features",
                "db_table": "batch_CVD_Risk_Model_Features",
                "unique_together": {("model", "feature")},
            },
        ),
        migrations.CreateModel(
            name="CVD_risk_Clinician_Patient",
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
                ("assigned_date", models.DateTimeField(auto_now_add=True)),
                (
                    "clinician",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.clinicians",
                    ),
                ),
                (
                    "patient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.patients",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Clinician Patients",
                "db_table": "CVD_risk_Clinician_Patient",
                "unique_together": {("clinician", "patient")},
            },
        ),
    ]
