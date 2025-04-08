# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Admins(models.Model):
    admin_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(unique=True, max_length=100)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Admins'
        verbose_name_plural = 'Admins'

class ClinicianPatient(models.Model):
    clinician = models.OneToOneField('Clinicians', models.DO_NOTHING, primary_key=True)  # The composite primary key (clinician_id, patient_id) found, that is not supported. The first column is selected.
    patient = models.ForeignKey('Patients', models.DO_NOTHING)
    assigned_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Clinician_Patient'
        unique_together = (('clinician', 'patient'),)
        verbose_name_plural = 'Clinician patients'

class Clinicians(models.Model):
    clinician_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(unique=True, max_length=100)
    password_hash = models.CharField(max_length=255)
    specialty = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    admin = models.ForeignKey(Admins, models.DO_NOTHING, blank=True, null=True)
    user = models.OneToOneField('Users', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Clinicians'
        verbose_name_plural = 'Clinicians'

class MlModels(models.Model):
    model_id = models.AutoField(primary_key=True)
    method = models.CharField(max_length=100)
    title = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'ML_Models'
        verbose_name_plural = 'ML Models'

class PatientOutcomes(models.Model):
    outcome_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey('Patients', models.DO_NOTHING, blank=True, null=True)
    outcome_description = models.TextField()
    reported_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Patient_Outcomes'
        verbose_name_plural = 'Patient outcomes'



class Patients(models.Model):
    patient_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(unique=True, max_length=100)
    password_hash = models.CharField(max_length=255)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    admin = models.ForeignKey(Admins, models.DO_NOTHING, blank=True, null=True)
    user = models.OneToOneField('Users', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Patients'
        verbose_name_plural = 'Patients'

class Questionnaire(models.Model):
    question_id = models.AutoField(primary_key=True)
    question_text = models.TextField()
    category = models.CharField(max_length=100, blank=True, null=True)
    dependencies = models.TextField(blank=True, null=True)
    admin = models.ForeignKey(Admins, models.DO_NOTHING, blank=True, null=True)
    question_order = models.IntegerField()
    response_type = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Questionnaire'
        verbose_name_plural = 'Questionnaires'


class Responses(models.Model):
    response_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patients, models.DO_NOTHING, blank=True, null=True)
    question = models.ForeignKey(Questionnaire, models.DO_NOTHING, blank=True, null=True)
    #Use one of these depending on response_type
    selected_option = models.ForeignKey('QuestionResponseOptions', models.DO_NOTHING, blank=True, null=True)
    numeric_response = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    text_answer = models.TextField(blank=True, null=True)
    
    response_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Responses'
        verbose_name_plural = 'Responses'


class RiskStratification(models.Model):
    stratification_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patients, models.DO_NOTHING, blank=True, null=True)
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    recommendation = models.TextField(blank=True, null=True)
    assessed_at = models.DateTimeField(blank=True, null=True)
    model = models.ForeignKey(MlModels, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Risk_Stratification'

class QuestionResponseOptions(models.Model): # This table allows us to define, for each question, all the possible options
    option_id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Questionnaire, models.DO_NOTHING)
    option_text = models.CharField(max_length=255)
    value = models.IntegerField(blank=True, null=True)  # Optional: use for scoring
    display_order = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Question_Response_Options'
        verbose_name_plural = 'Question response options'



class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    email = models.CharField(unique=True, max_length=255)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=9)

    class Meta:
        managed = False
        db_table = 'Users'
        verbose_name_plural = 'Users'



class AccountsUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()
    role = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'accounts_user'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('AccountsUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'
