from django.contrib import admin
from .models import (
    Patients,
    Clinicians,
    CVD_risk_Clinician_Patient,
    Users,
    CVD_risk_Questionnaire,
    CVD_risk_QuestionResponseOptions,
    CVD_risk_Responses,
    CVD_risk_Patient_Outcomes,
    Risk_Stratification,
    ML_Models,
    BatchCVDRiskFeature,
    BatchPredictionRun,
    BatchPredictionResultDetail,
    batch_CVD_Risk_Output,
)

admin.site.register(Patients)
admin.site.register(Clinicians)
admin.site.register(CVD_risk_Clinician_Patient)
admin.site.register(Users)
admin.site.register(CVD_risk_Questionnaire)
admin.site.register(CVD_risk_QuestionResponseOptions)
admin.site.register(CVD_risk_Responses)
admin.site.register(CVD_risk_Patient_Outcomes)
admin.site.register(Risk_Stratification)
admin.site.register(ML_Models)
admin.site.register(BatchCVDRiskFeature)
admin.site.register(BatchPredictionRun)
admin.site.register(BatchPredictionResultDetail)
admin.site.register(batch_CVD_Risk_Output)

