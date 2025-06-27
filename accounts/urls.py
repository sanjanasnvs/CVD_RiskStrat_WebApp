from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from accounts.views import assessment_view


urlpatterns = [
    path('starter/', views.home_view, name='starter-page'),
    path('learn-cvd/', views.learn_cvd, name='learn_cvd'),
    path('request-access/', views.request_access_view, name='request_access'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('clinician/dashboard/', views.patient_risk_panel, name='patient_risk_panel'),
    path('signup/', views.signup_view, name='signup'),
    path('dashboard/', views.role_based_dashboard_redirect, name='dashboard_redirect'),

    #  Password Reset URLs
    path('password_reset/', 
auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), 
name='password_reset'),
    path('password_reset/done/', 
auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), 
name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), 
name='password_reset_confirm'),
    path('reset/done/', 
auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), 
name='password_reset_complete'),

    # Admin views URLs
    path('admin/login/', views.admin_login_view, name='admin_login'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Patient views URLs
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('patient/assessment/', views.assessment_view, name='start_assessment'),
    path('patient/<int:patient_id>/results/', views.clinician_patient_results, name='clinician_patient_results'),
    path('patient/results/', views.patient_self_results, name='patient_self_results'),
    path('patient/history/', views.assessment_history, name='assessment_history'),
    path('patient/history/<uuid:submission_id>/', views.view_results_by_submission, name='view_results_by_submission'),
    #path('patient/learn/', views.patient_learn, name='patient_learn'),


    # Mohammed's views URLs
    path('clinician/batch-prediction/', views.batch_prediction, name='batch_prediction'),
    path('clinician/prediction-results/', views.prediction_results_view, name='prediction_results'),
    path('download-all-data/', views.download_all_data, name='download_all_data'),
    path('clinician/download-single-patient-data/<int:patient_index>/', views.download_single_patient_data, name='download_single_patient_data'),
    path('clinician/download-filtered-data/', views.download_filtered_data, name='download_filtered_data'),
    path('clinician/process-pending-batch/', views.process_pending_batch, name='process_pending_batch'),
    #path('clinician/ssreset-batch-prediction/', views.reset_batch_prediction, name='reset_batch_prediction'),
    path('admin-panel/', views.admin_panel, name='admin_panel')

]

