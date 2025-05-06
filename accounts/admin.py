from django.contrib import admin
from .models import (
    Patients,
    Clinicians,
    Admins,
    CVD_risk_Clinician_Patient,
    User,
    CVD_risk_Questionnaire,
    CVD_risk_QuestionResponseOptions,
    CVD_risk_Responses,
    CVD_risk_Patient_Outcomes,
    Risk_Stratification,
    ML_Models,
    batch_CVD_Risk_Features,
    batch_CVD_Risk_Model_Features,
    batch_CVD_Risk_Risk,
    batch_CVD_Risk_Output,
)

admin.site.register(Patients)
admin.site.register(Clinicians)
admin.site.register(Admins)
admin.site.register(CVD_risk_Clinician_Patient)
admin.site.register(User)
admin.site.register(CVD_risk_Questionnaire)
admin.site.register(CVD_risk_QuestionResponseOptions)
admin.site.register(CVD_risk_Responses)
admin.site.register(CVD_risk_Patient_Outcomes)
admin.site.register(Risk_Stratification)
admin.site.register(ML_Models)
admin.site.register(batch_CVD_Risk_Features)
admin.site.register(batch_CVD_Risk_Model_Features)
admin.site.register(batch_CVD_Risk_Risk)
admin.site.register(batch_CVD_Risk_Output)

