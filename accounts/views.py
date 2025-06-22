from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from .models import Users
from .forms import CustomUserCreationForm
from .models import *
from django.shortcuts import get_object_or_404
import joblib
import pandas as pd
import numpy as np
from django.http import JsonResponse
from django.db import DatabaseError
from django.db import transaction, connection
from django.views.decorators.http import require_http_methods
from .utils import should_display_question
from datetime import datetime
import os


thresholds = pd.read_csv("model_files/FinalSolFront1 (1).csv").iloc[0]
CATEGORY_THRESHOLDS = {
    "Sociodemographics": (thresholds["Min_Threshold1"], thresholds["Max_Threshold1"]),
    "Health and medical history": (thresholds["Min_Threshold2"], thresholds["Max_Threshold2"]),
    "Sex-specific factors": (thresholds["Min_Threshold3"], thresholds["Max_Threshold3"]),
    # add others as needed
}
CATEGORY_ORDER = ["Sociodemographics", "Health and medical history", "Sex-specific factors",
                  "Early life factors", "Family history", "Lifestyle and environment",
                  "Psychosocial factors"]

def get_risk_category(score, category):
    """
    Determines patient's risk category based on the score and thresholds.
    """
    try:
        idx = CATEGORY_ORDER.index(category) + 1  # because threshold columns are 1-indexed
        min_t = thresholds[f"Min_Threshold{idx}"]
        max_t = thresholds[f"Max_Threshold{idx}"]

        if score < min_t:
            return "Low Risk"
        elif score > max_t:
            return "High Risk"
        else:
            return "Inconclusive"
    except Exception as e:
        print(f"❌ Failed to classify risk: {e}")
        return "Unknown"

MODEL_FILE_MAPPING = {
    "Sociodemographics": "model_files/ML_models/MRMR_COX_Sociodemographics.pkl",
    "Health and medical history": "model_files/ML_models/MRMR_COX_Sociodemographics_Health_and_medical_history.pkl",
    "Sex-specific factors": "model_files/ML_models/MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors.pkl",
    "Early life factors": "model_files/ML_models/MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors.pkl",
    "Family history": "model_files/ML_models/MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history.pkl",
    "Lifestyle and environment": "model_files/ML_models/MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history_Lifestyle_and_environment.pkl",
    "Psychosocial factors": "model_files/ML_models/MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history_Lifestyle_and_environment_Psychosocial_factors.pkl",
}

MODEL_DB_NAME_MAPPING = {
    'model1_sociodemographic': 'MRMR_COX_Sociodemographics.pkl',
    'model2_healthandmed': 'MRMR_COX_Sociodemographics_Health_and_medical_history.pkl',
    'model3_SSF': 'MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors',
    'model4_early_life': 'MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors.pkl',
    'model5_family_history': 'MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history.pkl',
    'model6_lifestyle': 'MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history_Lifestyle_and_environment.pkl',
    'model7_biggestmodel': 'MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history_Lifestyle_and_environment_Psychosocial_factors.pkl'
}



def login_view(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            if user.role == 'patient':
                return redirect('patient_dashboard')
            elif user.role == 'clinician_approved':
                return redirect('clinician_dashboard')
            elif user.role == 'admin':
                return redirect('/admin/')  # built-in admin site
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'users/login.html')

# Shows a login page for admin, checks if the user is logged in with role = 'admin', and if so, takes them to the admin dashboard
def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.role == 'admin':
            login(request, user)
            return redirect('admin_dashboard')
        else:
            return render(request, 'admin/login.html', {'error': 'Invalid credentials or not an admin'})
    return render(request, 'admin/login.html')

# Checks if the user is logged in and is an admin, and if so, shows them a list of all users, questionnaires and responses
def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    users = CustomUser.objects.all()
    questionnaires = Questionnaire.objects.all()
    responses = Response.objects.all()
    return render(request, 'admin/dashboard.html', {
        'users': users,
        'questionnaires': questionnaires,
        'responses': responses
    })

@login_required
def role_based_dashboard_redirect(request):
    if request.user.role == 'patient':
        return redirect('patient_dashboard')
    elif request.user.role == 'clinician':
        return redirect('clinician_dashboard')
    else:
        return redirect('/admin/')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Patients, CVD_risk_Questionnaire, CVD_risk_Responses, CVD_risk_Patient_Outcomes

@login_required
def patient_dashboard(request):
    if request.user.role != 'patient':
        return redirect('home')  # or show a 403
    # Fetch the patient profile for this user
    patient_profile = get_object_or_404(Patients, user=request.user)

    context = {
        'patient': patient_profile
    }
    return render(request, 'patients/dashboard.html')
	
from django.shortcuts import render, redirect
from accounts.models import CVD_risk_Questionnaire, CVD_risk_QuestionResponseOptions, CVD_risk_Responses
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from uuid import uuid4
from feature_calculators import (
    model1_sociodemographic,
    model2_healthandmed,
    model3_SSF,
    model4_early_life,
    model5_family_history,
    model6_lifestyle,
    model7_biggestmodel
)

import joblib
from datetime import datetime



from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import connection, DatabaseError
from uuid import uuid4
from datetime import datetime
import os
import joblib

from .models import (
    CVD_risk_Questionnaire,
    CVD_risk_QuestionResponseOptions,
    CVD_risk_Responses,
    Patients,
    ML_Models,
    Risk_Stratification
)
from .utils import should_display_question
from Questionnaire_data.utils import get_visible_questions_for_patient_in_category

# 🧠 Optional helper for message text
def get_final_message_text(risk_category):
    if risk_category == "Low Risk":
        return "✅ You are at low 10-year risk of CVD. Please maintain a healthy lifestyle."
    elif risk_category == "High Risk":
        return "⚠️ You are at high 10-year risk of CVD. Please contact your GP or clinician for further testing."
    else:
        return "❓ Risk inconclusive. Continue to next section."



@require_http_methods(["GET", "POST"])
@login_required
def assessment_view(request):
    from django.db import connection
    from django.db.models import Max

    category = request.GET.get('category')
    error_message = None

    # Ordered form category flow
    CATEGORY_ORDER = [
        "Sociodemographics",
        "Health and medical history",
        "Sex-specific factors",
        "Early life factors",
        "Family history",
        "Lifestyle and environment",
        "Psychosocial factors"
    ]

    # Category to function and model mapping
    CATEGORY_MODEL_MAPPING = {
        "Sociodemographics": model1_sociodemographic,
        "Health and medical history": model2_healthandmed,
        "Sex-specific factors": model3_SSF,
        "Early life factors": model4_early_life,
        "Family history": model5_family_history,
        "Lifestyle and environment": model6_lifestyle,
        "Psychosocial factors": model7_biggestmodel
    }

    MODEL_FILE_MAPPING = {
        "Sociodemographics": "model_files/ML_models/MRMR_COX_Sociodemographics.pkl",
        "Health and medical history": "model_files/ML_models/MRMR_COX_Sociodemographics_Health_and_medical_history.pkl",
        "Sex-specific factors": "model_files/ML_models/MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors.pkl",
        "Early life factors": "model_files/ML_models/MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors.pkl",
        "Family history": "model_files/ML_models/MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history.pkl",
        "Lifestyle and environment": "model_files/ML_models/MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history_Lifestyle_and_environment.pkl",
        "Psychosocial factors": "model_files/ML_models/MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history_Lifestyle_and_environment_Psychosocial_factors.pkl",
    }

    raw_categories = CVD_risk_Questionnaire.objects.values_list('category', flat=True).distinct()
    all_categories = sorted(set(raw_categories), key=lambda x: CATEGORY_ORDER.index(x) if x in CATEGORY_ORDER else 999)

    # Redirect to first unanswered category
    if not category and all_categories:
        return redirect(f"{reverse('start_assessment')}?category={all_categories[0]}")

    try:
        current_index = all_categories.index(category)
        previous_category = all_categories[current_index - 1] if current_index > 0 else None
        next_category = all_categories[current_index + 1] if current_index + 1 < len(all_categories) else None
    except ValueError:
        previous_category = None
        next_category = None

    patient = Patients.objects.get(user=request.user)

    all_questions = CVD_risk_Questionnaire.objects.filter(category=category).order_by('question_order')
    visible_questions = get_visible_questions_for_patient_in_category(patient, category)

    # Load latest saved responses to prefill
    saved_responses = {
        r.question.question_id: (
            r.option_selected.encoded_value if r.option_selected else
            r.numeric_response if r.numeric_response is not None else
            r.boolean_response
        )
        for r in CVD_risk_Responses.objects.filter(patient=patient)
    }

    # ---------- Handle POST (Form Submission) ----------
    if request.method == 'POST':
        try:
            # Assign a new submission session if not yet set
            if 'submission_id' not in request.session:
                request.session['submission_id'] = str(uuid4())
            submission_id = request.session['submission_id']

            for q in visible_questions:
                key = f"question_{q.question_id}"
                options = CVD_risk_QuestionResponseOptions.objects.filter(question=q)

                # Multi-select handling
                if q.answer_type == "Toggle multiple answer":
                    values = request.POST.getlist(f"{key}_option")
                    if not values:
                        continue
                    selected_options = options.filter(id__in=values)
                    if not selected_options.exists():
                        continue
                    response_obj = CVD_risk_Responses.objects.create(
                        patient=patient, question=q, response_type=q.answer_type, submission_id=submission_id
                    )
                    response_obj.multi_selected_options.set(selected_options)
                    response_obj.save()
                    continue

                # Single/miscellaneous responses
                value = request.POST.get(key)
                if not value or value.lower() in ['select one answer', 'choose', '']:
                    continue

                response_obj = CVD_risk_Responses.objects.create(
                    patient=patient, question=q, response_type=q.answer_type, submission_id=submission_id
                )

                if options.exists():
                    try:
                        selected_option = options.get(id=int(value))
                        response_obj.option_selected = selected_option
                    except:
                        continue
                else:
                    try:
                        response_obj.numeric_response = float(value)
                    except:
                        response_obj.boolean_response = value.lower() in ['yes', 'true', '1']
                response_obj.save()

        except DatabaseError:
            connection.rollback()
            messages.error(request, "Database error occurred.")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            messages.error(request, "Unexpected error occurred.")

        # Proceed only if at least one response was saved
        if CVD_risk_Responses.objects.filter(patient=patient, question__category=category, submission_id=submission_id).exists():
            completed = request.session.get('completed_categories', [])
            if category not in completed:
                completed.append(category)
                request.session['completed_categories'] = completed

            # ---------- Model Evaluation ----------
            if category in CATEGORY_MODEL_MAPPING:
                model_module = CATEGORY_MODEL_MAPPING[category]
                try:
                    df_scaled = model_module.calculate_features(patient.patient_id, submission_id)
                    model_path = MODEL_FILE_MAPPING[category]
                    print(f"🧠 Looking for model: {model_path}")

                    if not os.path.exists(model_path):
                        raise FileNotFoundError(f"Model file not found for category: {category}")

                    model = joblib.load(model_path)
                    print("🧾 Final columns before prediction:", df_scaled.columns.tolist())

                    risk_score = float(model.predict(df_scaled)[0])
                    print(f"📈 Risk score = {risk_score:.2f}")

                    risk_category = get_risk_category(risk_score, category)
                    print(f"🧪 Risk classification: {risk_category}")

                    model_name_cleaned = os.path.basename(model_path).replace(".pkl", "")
                    model_obj = ML_Models.objects.get(model_name=model_name_cleaned)

                    # Save results with timestamp for grouping later
                    assessed_time = datetime.now()
                    Risk_Stratification.objects.create(
                        patient=patient,
                        model=model_obj,
                        assessed_at=assessed_time,
                        risk_score=risk_score,
                        recommendation=risk_category,
                        submission_id=submission_id
                    )

                    # Early stopping — render final message if conclusive result reached
                    if risk_category in ["Low Risk", "High Risk"]:
                        request.session.pop("submission_id", None)
                        return render(request, "patients/final_message.html", {
                            "risk_score": risk_score,
                            "recommendation": risk_category,
                            "message": get_final_message_text(risk_category)
                        })

                except Exception as e:
                    print(f"❌ Error during model execution for {category}: {e}")

            # Only clear submission_id at end of full or early-stopped run
            if risk_category in ["Low Risk", "High Risk"] or not next_category:
                request.session.pop("submission_id", None)

            if next_category:
                return redirect(f"{reverse('start_assessment')}?category={next_category}")
            else:
                request.session['completed_categories'] = []
                return redirect('patient_results')
        else:
            error_message = "Please answer at least one question before proceeding."

    # ---------- GET View ----------
    question_data = []
    for q in visible_questions:
        options = list(CVD_risk_QuestionResponseOptions.objects.filter(question=q))
        latest = CVD_risk_Responses.objects.filter(patient=patient, question=q).order_by('-last_updated').first()

        response_value = None
        response_id = None
        multi_ids = []
        if latest:
            if q.answer_type == "Enter integer answer":
                response_value = latest.numeric_response
            elif q.answer_type == "Select one answer":
                response_id = str(latest.option_selected_id) if latest.option_selected_id else None
            elif q.answer_type == "Toggle multiple answer":
                multi_ids = latest.multi_selected_options.values_list('id', flat=True)

        question_data.append({
            'question': q,
            'options': options,
            'response': response_value,
            'response_id': response_id,
            'multi_response_ids': multi_ids,
            'answer_type': q.answer_type
        })

    return render(request, 'patients/assessment.html', {
        'category': category,
        'question_data': question_data,
        'all_categories': all_categories,
        'completed_categories': request.session.get('completed_categories', []),
        'previous_category': previous_category,
        'next_category': next_category,
        'error_message': error_message
    })




def get_next_category(category_list, current):
    """Helper function to get the next category in the list"""
    try:
        idx = category_list.index(current)
        return category_list[idx + 1] if idx + 1 < len(category_list) else None
    except ValueError:
        return None


MODEL_METRICS = {
    "MRMR_COX_Sociodemographics": {
        "accuracy": "16.26%",
        "auroc": "0.6473",
        "precision": "16.26%",
        "recall": "100.00%"
    },
    "MRMR_COX_Sociodemographics_Health_and_medical_history": {
        "accuracy": "86.77%",
        "auroc": "0.7785",
        "precision": "91.49%",
        "recall": "24.94%"
    },
    "MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors": {
        "accuracy": "86.85%",
        "auroc": "0.7920",
        "precision": "96.19%",
        "recall": "17.93%"
    },
    "MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors": {
        "accuracy": "86.82%",
        "auroc": "0.7917",
        "precision": "96.12%",
        "recall": "18.51%"
    },
    "MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history": {
        "accuracy": "86.56%",
        "auroc": "0.7862",
        "precision": "87.13%",
        "recall": "26.86%"
    },
    "MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history_Lifestyle_and_environment": {
        "accuracy": "86.59%",
        "auroc": "0.7946",
        "precision": "97.31%",
        "recall": "12.39%"
    },
    "MRMR_COX_Sociodemographics_Health_and_medical_history_Sex-specific_factors_Early_life_factors_Family_history_Lifestyle_and_environment_Psychosocial_factors": {
        "accuracy": "86.59%",
        "auroc": "0.7942",
        "precision": "97.25%",
        "recall": "12.90%"
    }
}




@login_required
def patient_self_results(request):
    if request.user.role != 'patient':
        return redirect('home')

    patient = get_object_or_404(Patients, user=request.user)

    # STEP 1: Find the latest submission ID used by this patient
    latest_strat = Risk_Stratification.objects.filter(patient=patient).exclude(submission_id__isnull=True).order_by('-assessed_at').first()

    if not latest_strat:
        return render(request, 'patients/results.html', {
            'patient': patient,
            'model_results': [],
            'all_models_inconclusive': True,
            'all_categories_completed': False,
            'assessment_date': None
        })

    latest_submission_id = latest_strat.submission_id
    assessment_date = latest_strat.assessed_at

    # STEP 2: Fetch only results for models evaluated in this session
    strat_results = Risk_Stratification.objects.filter(
        patient=patient,
        submission_id=latest_submission_id
    ).select_related('model').order_by('assessed_at')

    model_results = []
    all_models_inconclusive = True

    for strat in strat_results:
        category_guess = strat.model.model_name.replace("MRMR_COX_", "").replace("_", " ").strip().title()
        if strat.recommendation in ['Low Risk', 'High Risk']:
            all_models_inconclusive = False

        model_results.append({
            'category': category_guess,
            'prediction_score': round(strat.risk_score, 2),
            'risk_category': strat.recommendation,
            'plot_path': f"patient_plots/patient_{patient.patient_id}_{strat.model.model_name}.png",
            **MODEL_METRICS.get(strat.model.model_name, {
                "accuracy": "N/A",
                "auroc": "N/A",
                "precision": "N/A",
                "recall": "N/A"
                })
            })

    return render(request, 'patients/results.html', {
        'patient': patient,
        'model_results': model_results,
        'all_models_inconclusive': all_models_inconclusive,
        'all_categories_completed': len(model_results) == len(CATEGORY_ORDER),
        'assessment_date': assessment_date,
    })




@login_required
def clinician_patient_results(request, patient_id=None):
    # Step 1: Determine the patient based on role
    if request.user.role == 'patient':
        patient = get_object_or_404(Patients, user=request.user)
    elif request.user.role == 'clinician_approved':
        if not patient_id:
            return redirect('clinician_dashboard')
        patient = get_object_or_404(Patients, id=patient_id)
    else:
        return redirect('home')

    # Step 2: Fetch only the completed models (not all 7)
    results = []
    try:
        # Get all stratification results for this patient, ordered latest first
        strat_results = (
            Risk_Stratification.objects.filter(patient=patient)
            .select_related("model")
            .order_by("-assessed_at")
        )

        # Track the models already included
        seen_model_names = set()

        for strat in strat_results:
            model = strat.model
            model_name = model.model_name
            if model_name in seen_model_names:
                continue  # Avoid duplicates if multiple entries exist
            seen_model_names.add(model_name)

            # Derive category name from mapping
            category = None
            for k, v in MODEL_FILE_MAPPING.items():
                if os.path.basename(v).replace(".pkl", "") == model_name:
                    category = k
                    break

            if not category:
                continue  # Skip if mapping fails

            results.append({
                'category': category,
                'score': round(strat.risk_score, 2),
                'risk': strat.recommendation,
                'plot_path': f"/static/patient_plots/patient_{patient.id}_{model_name}.png",
                **MODEL_METRICS.get(model_name, {
                    "accuracy": "N/A",
                    "auroc": "N/A",
                    "precision": "N/A",
                    "recall": "N/A"
                    })
                })

    except Exception as e:
        print(f"⚠️ Error processing results: {e}")

    return render(request, 'patients/results.html', {
        'patient': patient,
        'model_results': results
    })



@login_required
def assessment_history(request):
    if request.user.role != 'patient':
        return redirect('home')
    return render(request, 'patients/history.html')

@login_required
def patient_learn(request):
    return render(request, 'learn.html')


@login_required
def clinician_dashboard(request):
    if request.user.role != 'clinician_approved':
        return redirect('home')

    clinician = Clinicians.objects.get(user=request.user)
    assignments = CVD_risk_Clinician_Patient.objects.filter(clinician=clinician).select_related('patient')

    patient_data = []
    high_risk_patients = []
    
    for assign in assignments:
        patient = assign.patient
        latest_risk = Risk_Stratification.objects.filter(patient=patient).order_by('-assessed_at').first()
        
        is_high_risk = latest_risk and latest_risk.recommendation == 'High Risk'
        
        patient_info = {
            'patient_id': patient.patient_id,  # Add this for URL routing
            'name': f"{patient.user.first_name} {patient.user.last_name}",
            'dob': patient.date_of_birth,
            'email': patient.user.email,
            'risk_score': latest_risk.risk_score if latest_risk else None,
            'recommendation': latest_risk.recommendation if latest_risk else None,
            'assessed_at': latest_risk.assessed_at if latest_risk else None,
            'is_high_risk': is_high_risk,
        }
        
        patient_data.append(patient_info)
        if is_high_risk:
            high_risk_patients.append(patient_info)

    # Calculate statistics
    total_patients = len(patient_data)
    high_risk_count = len([p for p in patient_data if p.get('recommendation') == 'High Risk'])
    intermediate_risk_count = len([p for p in patient_data if p.get('recommendation') == 'Intermediate Risk'])
    low_risk_count = len([p for p in patient_data if p.get('recommendation') == 'Low Risk'])

    return render(request, 'clinicians/clinician_dashboard.html', {
        'patient_data': patient_data,
        'high_risk_patients': high_risk_patients,
        'total_patients': total_patients,
        'high_risk_count': high_risk_count,
        'intermediate_risk_count': intermediate_risk_count,
        'low_risk_count': low_risk_count,
    })



def logout_view(request):
    logout(request)
    return redirect('login')

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            sex = form.cleaned_data.get('sex')
            login(request, user)
            return redirect('patient_dashboard')
        else:
            print(" Form errors:", form.errors)
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', {'form': form})



# Create your views here.
def home_view(request):
    return render(request, 'medilab/starter-page.html')

def request_access_view(request):
    return render(request, 'users/request-access.html')
