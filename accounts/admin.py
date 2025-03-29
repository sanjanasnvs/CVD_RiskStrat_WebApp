from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .legacy_models import Patients, Clinicians, Admins, ClinicianPatient, Users, Questionnaire, Responses, PatientOutcomes, RiskStratification, MlModels


admin.site.register(Patients)
admin.site.register(Clinicians)
admin.site.register(Admins)
admin.site.register(ClinicianPatient)
admin.site.register(Users)
admin.site.register(Questionnaire)
admin.site.register(Responses)
admin.site.register(PatientOutcomes)
admin.site.register(RiskStratification)
admin.site.register(MlModels)

# Register your models here.
