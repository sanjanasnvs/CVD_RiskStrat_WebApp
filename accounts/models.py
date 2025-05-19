from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
    
    #  Important: This ensures MySQL ENUM doesn't complain
        extra_fields.setdefault('role', 'clinician_approved')

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class Users(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)  # Required for access to admin
    is_superuser = models.BooleanField(default=True)  # Required for superuser privileges

    role = models.CharField(
        max_length=20,
        choices=[
            ('patient', 'Patient'),
            ('clinician_pending', 'Clinician Pending'),
            ('clinician_approved', 'Clinician Approved')
        ]
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    #  Plug in the custom manager here
    objects = CustomUserManager()

    class Meta:
        db_table = 'Users'
        verbose_name_plural = 'Users'


class Patients(models.Model):
    patient_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Patients'
        verbose_name_plural = 'Patients'


class Clinicians(models.Model):
    clinician_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    specialty = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Clinicians'
        verbose_name_plural = 'Clinicians'


class CVD_risk_Questionnaire(models.Model):
    question_id = models.AutoField(primary_key=True)
    question_text = models.TextField()
    category = models.CharField(max_length=100, null=True, blank=True)
    subcategory = models.CharField(max_length=100, null=True, blank=True)
    dependencies = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    question_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'CVD_risk_Questionnaire'
        verbose_name_plural = 'CVD Risk Questionnaire'


class CVD_risk_QuestionResponseOptions(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(CVD_risk_Questionnaire, on_delete=models.CASCADE)
    option_text = models.TextField()
    value_range_start = models.FloatField(null=True, blank=True)
    value_range_end = models.FloatField(null=True, blank=True)
    option_label = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'CVD_risk_QuestionResponseOptions'
        verbose_name_plural = 'Questionnaire Response Options'


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
        verbose_name_plural = 'CVD Risk Responses'


class CVD_risk_Clinician_Patient(models.Model):
    clinician = models.ForeignKey(Clinicians, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    assigned_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'CVD_risk_Clinician_Patient'
        unique_together = (('clinician', 'patient'),)
        verbose_name_plural = 'Clinician Patients'


class ML_Models(models.Model):
    model_id = models.AutoField(primary_key=True)
    model_name = models.CharField(max_length=255)
    model_type = models.CharField(max_length=100)

    class Meta:
        db_table = 'ML_Models'
        verbose_name_plural = 'ML Models'


class batch_CVD_Risk_Features(models.Model):
    feature_id = models.AutoField(primary_key=True)
    feature_name = models.CharField(max_length=255)
    feature_description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'batch_CVD_Risk_Features'
        verbose_name_plural = 'Batch CVD Risk Features'


class batch_CVD_Risk_Model_Features(models.Model):
    model = models.ForeignKey(ML_Models, on_delete=models.CASCADE)
    feature = models.ForeignKey(batch_CVD_Risk_Features, on_delete=models.CASCADE)

    class Meta:
        db_table = 'batch_CVD_Risk_Model_Features'
        unique_together = (('model', 'feature'),)
        verbose_name_plural = 'Batch CVD Risk Model Features'


class Risk_Stratification(models.Model):
    stratification_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    risk_score = models.DecimalField(max_digits=5, decimal_places=2)
    recommendation = models.TextField()
    assessed_at = models.DateTimeField(auto_now_add=True)
    model = models.ForeignKey(ML_Models, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'Risk_Stratification'
        verbose_name_plural = 'Risk Stratification'


class CVD_risk_Patient_Outcomes(models.Model):
    outcome_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    outcome_description = models.TextField()
    reported_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'CVD_risk_Patient_Outcomes'
        verbose_name_plural = 'CVD Risk Patient Outcomes'


class batch_CVD_Risk_Risk(models.Model):
    risk_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patients, on_delete=models.CASCADE)
    model = models.ForeignKey(ML_Models, on_delete=models.CASCADE)
    risk_score = models.DecimalField(max_digits=5, decimal_places=2)
    prediction_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'batch_CVD_Risk_Risk'
        verbose_name_plural = 'Batch CVD Risk Risk'


class batch_CVD_Risk_Output(models.Model):
    output_id = models.AutoField(primary_key=True)
    risk = models.ForeignKey(batch_CVD_Risk_Risk, on_delete=models.CASCADE)
    plot_type = models.CharField(max_length=100)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'batch_CVD_Risk_Output'
        verbose_name_plural = 'Batch CVD Risk Output'

