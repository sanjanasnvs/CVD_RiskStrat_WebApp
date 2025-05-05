
from django.db import models


class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=10)

    class Meta:
        db_table = 'Users'


class Admins(models.Model):
    admin_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Admins'


class Patients(models.Model):
    patient_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), 
('Other', 'Other')], null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    admin = models.ForeignKey(Admins, on_delete=models.SET_NULL, null=True)
    user = models.OneToOneField(Users, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Patients'


class Clinicians(models.Model):
    clinician_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=255)
    specialty = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    admin = models.ForeignKey(Admins, on_delete=models.SET_NULL, null=True)
    user = models.OneToOneField(Users, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Clinicians'


class CVD_risk_Questionnaire(models.Model):
    question_id = models.AutoField(primary_key=True)
    question_text = models.TextField()
    category = models.CharField(max_length=100, null=True, blank=True)
    subcategory = models.CharField(max_length=100, null=True, blank=True)
    dependencies = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    question_order = models.IntegerField(default=0)
    admin = models.ForeignKey(Admins, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'CVD_risk_Questionnaire'


class CVD_risk_QuestionResponseOptions(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(CVD_risk_Questionnaire, on_delete=models.CASCADE)
    option_text = models.TextField()
    value_range_start = models.FloatField(null=True, blank=True)
    value_range_end = models.FloatField(null=True, blank=True)
    option_label = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'CVD_risk_QuestionResponseOptions'


class CVD_risk_Responses(models.Model):
    response_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    question = models.ForeignKey(CVD_risk_Questionnaire, on_delete=models.CASCADE)
    response_type = models.CharField(max_length=50)
    numeric_response = models.FloatField(null=True, blank=True)
    boolean_response = models.BooleanField(null=True, blank=True)
    option_selected = models.ForeignKey(CVD_risk_QuestionResponseOptions, 
on_delete=models.SET_NULL, null=True, blank=True)
    response_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'CVD_risk_Responses'


class CVD_risk_Clinician_Patient(models.Model):
    clinician = models.ForeignKey(Clinicians, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    assigned_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'CVD_risk_Clinician_Patient'
        unique_together = (('clinician', 'patient'),)


class ML_Models(models.Model):
    model_id = models.AutoField(primary_key=True)
    model_name = models.CharField(max_length=255)
    model_type = models.CharField(max_length=100)

    class Meta:
        db_table = 'ML_Models'


class batch_CVD_Risk_Features(models.Model):
    feature_id = models.AutoField(primary_key=True)
    feature_name = models.CharField(max_length=255)
    feature_description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'batch_CVD_Risk_Features'


class batch_CVD_Risk_Model_Features(models.Model):
    model = models.ForeignKey(ML_Models, on_delete=models.CASCADE)
    feature = models.ForeignKey(batch_CVD_Risk_Features, on_delete=models.CASCADE)

    class Meta:
        db_table = 'batch_CVD_Risk_Model_Features'
        unique_together = (('model', 'feature'),)


class Risk_Stratification(models.Model):
    stratification_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    risk_score = models.DecimalField(max_digits=5, decimal_places=2)
    recommendation = models.TextField()
    assessed_at = models.DateTimeField(auto_now_add=True)
    model = models.ForeignKey(ML_Models, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'Risk_Stratification'


class CVD_risk_Patient_Outcomes(models.Model):
    outcome_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    outcome_description = models.TextField()
    reported_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'CVD_risk_Patient_Outcomes'


class batch_CVD_Risk_Risk(models.Model):
    risk_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    model = models.ForeignKey(ML_Models, on_delete=models.CASCADE)
    risk_score = models.DecimalField(max_digits=5, decimal_places=2)
    prediction_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'batch_CVD_Risk_Risk'


class batch_CVD_Risk_Output(models.Model):
    output_id = models.AutoField(primary_key=True)
    risk = models.ForeignKey(batch_CVD_Risk_Risk, on_delete=models.CASCADE)
    plot_type = models.CharField(max_length=100)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'batch_CVD_Risk_Output'

