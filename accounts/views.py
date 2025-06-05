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
from utils import calculate_features_from_responses, should_display_question
from datetime import datetime


thresholds = pd.read_csv("model_files/FinalSolFront1 (1).csv").iloc[0]
CATEGORY_THRESHOLDS = {
    "Sociodemographics": (thresholds["Min_Threshold1"], thresholds["Max_Threshold1"]),
    "Health and medical history": (thresholds["Min_Threshold2"], thresholds["Max_Threshold2"]),
    "Sex-specific factors": (thresholds["Min_Threshold3"], thresholds["Max_Threshold3"]),
    # add others as needed
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

@require_http_methods(["GET", "POST"])
@login_required
def assessment_view(request):
    category = request.GET.get('category')
    error_message = None

    CATEGORY_ORDER = [
        "Sociodemographics", "Health and medical history", "Sex-specific factors",
        "Early life factors", "Family history", "Lifestyle and environment", "Psychosocial factors"
    ]

    # All categories available in the database (fixed order)
    raw_categories = CVD_risk_Questionnaire.objects.values_list('category', flat=True).distinct()
    all_categories = sorted(set(raw_categories), key=lambda x: CATEGORY_ORDER.index(x) if x in CATEGORY_ORDER else 999)

    if not category and all_categories:
        return redirect(f"{reverse('start_assessment')}?category={all_categories[0]}")

    # Navigation helpers
    try:
        current_index = all_categories.index(category)
        previous_category = all_categories[current_index - 1] if current_index > 0 else None
        next_category = all_categories[current_index + 1] if current_index + 1 < len(all_categories) else None
    except ValueError:
        previous_category = None
        next_category = None

    patient = Patients.objects.get(user=request.user)
    all_questions = CVD_risk_Questionnaire.objects.filter(category=category).order_by('question_order')

    saved_responses = {
        r.question.question_id: (r.option_selected_id or r.numeric_response or r.boolean_response)
        for r in CVD_risk_Responses.objects.filter(patient=patient)
    }

    visible_questions = [q for q in all_questions if should_display_question(q, saved_responses)]

    # ----- Handle POST Submission -----
    if request.method == 'POST':
        all_valid = True
        try:
            if connection.connection and not connection.is_usable():
                connection.close()

            for q in visible_questions:
                key = f"question_{q.question_id}"
                response_data = {}
                options = CVD_risk_QuestionResponseOptions.objects.filter(question=q)

                if q.answer_type == "Toggle multiple answer":
                    values = request.POST.getlist(f"{key}_option")
                    if not values:
                        all_valid = False
                        break
                    selected_options = CVD_risk_QuestionResponseOptions.objects.filter(id__in=values)
                    if not selected_options.exists():
                        all_valid = False
                        break
                    response_obj, _ = CVD_risk_Responses.objects.get_or_create(
                        patient=patient, question=q,
                        defaults={'response_type': q.answer_type}
                    )
                    response_obj.multi_selected_options.set(selected_options)
                    response_obj.response_type = q.answer_type
                    response_obj.save()
                    continue

                value = request.POST.get(key)
                if value is None or str(value).strip().lower() in ['select one answer', 'choose', ''] or str(value).strip() == "":
                    all_valid = False
                    break

                if options.exists():
                    try:
                        selected_option = options.get(id=int(value))
                        opt_text = selected_option.option_text.strip().lower()
                        if not opt_text or opt_text in ['select one answer', 'choose', '']:
                            raise ValueError("Invalid placeholder value selected.")
                        response_data['option_selected'] = selected_option
                        response_data['option_selected_id'] = selected_option.id
                    except (CVD_risk_QuestionResponseOptions.DoesNotExist, ValueError):
                        all_valid = False
                        break
                else:
                    try:
                        response_data['numeric_response'] = float(value)
                    except ValueError:
                        response_data['boolean_response'] = value.lower() in ['yes', 'true', '1']

                if not response_data:  # guard against saving blank responses
                    all_valid = False
                    break

                response_obj, _ = CVD_risk_Responses.objects.get_or_create(patient=patient, question=q)
                for k, v in response_data.items():
                    setattr(response_obj, k, v)
                response_obj.save()

        except DatabaseError:
            all_valid = False
            connection.rollback()
            messages.error(request, "Database error occurred. Please try again.")
        except Exception:
            all_valid = False
            messages.error(request, "Unexpected error occurred. Please try again.")

        if all_valid:
            completed = request.session.get('completed_categories', [])
            if category not in completed:
                completed.append(category)
                request.session['completed_categories'] = completed

            if category in CATEGORY_THRESHOLDS:
                # Prepare input
                responses = CVD_risk_Responses.objects.filter(patient=patient, question__category=category)
                response_dict = {}
                for r in responses:
                   q_text = r.question.question_text.strip().lower()  # Normalize question key
                   val = None

                   if r.numeric_response is not None:
                       val = r.numeric_response
                   elif r.boolean_response is not None:
                       val = 1 if r.boolean_response else 0
                   elif r.option_selected is not None:
                       opt = r.option_selected
                       opt_text = opt.option_text.strip().lower()
                       if opt_text not in ['select one answer', 'choose', '']:
                           val = opt.value_range_start


                   if val not in [None, '', 'select one answer', 'choose']:
                        response_dict[q_text] = val

                features = calculate_features_from_responses(response_dict)
                    

                # Load model + preprocessing
                print("🔍 Loading model files and preprocessing tools...")
                sample_df = pd.read_csv("model_files/correct_sociodemographics_sample.csv")
                if 'Unnamed: 0' in sample_df.columns:
                    sample_df = sample_df.drop(columns=['Unnamed: 0'])
                model = joblib.load("model_files/MRMR_COX_Sociodemographics.pkl")
                scaler = joblib.load("model_files/scaler.pkl")
                imputer = joblib.load("model_files/sociodemographics_rf (1).pkl")
                print("✅ Model and tools loaded successfully.")

                input_cols = imputer.feature_names_in_.tolist()
                features = calculate_features_from_responses(response_dict)
                aligned = {col: features.get(col, 0) for col in input_cols}
                print("🧮 Aligned model inputs:")
                for k, v in aligned.items():
                    print(f"  {k}: {v}")
 
                df = pd.DataFrame([aligned])
                print("🔎 Raw model inputs before imputation:")
                print(df.loc[:, (df != 0).any(axis=0)])
                X = scaler.transform(imputer.transform(df))
                print("✅ Finished imputation and scaling.")
                risk_score = float(model.predict(X)[0])
                print(f"📈 Calculated risk score for category '{category}': {risk_score:.4f}")

                # Fetch model object from ML_Models table
                try:
                    model_obj = ML_Models.objects.get(model_name="MRMR_COX_Sociodemographics")
                except ML_Models.DoesNotExist:
                    print("❌ Model not found in ML_Models table. Please run load_ml_models first.")
                    raise

                # Define thresholds and recommendations
                low_th, high_th = CATEGORY_THRESHOLDS[category]
                print(f"🔻 Thresholds -> Low: {low_th}, High: {high_th}")

                recommendation = (
                    "Low Risk" if risk_score < low_th else
                    "High Risk" if risk_score > high_th else
                    "Intermediate Risk"
                )

                # Save to DB
                Risk_Stratification.objects.create(
                    patient_id=patient.patient_id,
                    model_id=model_obj.model_id,  # foreign key referencing ML_Models table
                    assessed_at=datetime.now(),
                    risk_score=risk_score,
                    recommendation=recommendation  # Optional: will set below
                )
                print("✅ Risk score saved to DB for patient:", patient.user.username)


                if risk_score < low_th:
                    return render(request, "patients/final_message.html", {
                        "risk_score": risk_score,
                        "recommendation": "Low Risk",
                        "message": "Based on your responses, you are currently at low risk. You can view detailed results in your dashboard."
                    })
                elif risk_score > high_th:
                    return render(request, "patients/final_message.html", {
                        "risk_score": risk_score,
                        "recommendation": "High Risk",
                        "message": "Based on your responses, you are currently at high risk. Please consult your care provider. Full details are available in your dashboard."
                    })
                else:
                    return redirect(f"{reverse('start_assessment')}?category={next_category}")

            if next_category:
                return redirect(f"{reverse('start_assessment')}?category={next_category}")
            else:
                request.session['completed_categories'] = []
                return redirect('patient_results')

    # ----- GET Display -----
    question_data = []
    for q in visible_questions:
        options = list(CVD_risk_QuestionResponseOptions.objects.filter(question=q))
        saved = CVD_risk_Responses.objects.filter(patient=patient, question=q).first()

        response_value = None
        response_id = None
        multi_ids = []
        if saved:
            if q.answer_type == "Enter integer answer":
                response_value = saved.numeric_response
            elif q.answer_type == "Select one answer":
                response_id = str(saved.option_selected_id) if saved.option_selected_id else None
            elif q.answer_type == "Toggle multiple answer":
                multi_ids = saved.multi_selected_options.values_list('id', flat=True)

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


@login_required
def patient_self_results(request):
    if request.user.role != 'patient':
        return redirect('home')
    patient = get_object_or_404(Patient, user=request.user)
    return render(request, 'patients/results.html', {'patient': patient})


@login_required
def clinician_patient_results(request, patient_id=None):
    if request.user.role == 'patient':
        # Patients can only view their own results
        patient = get_object_or_404(Patient, user=request.user)
    elif request.user.role == 'clinician_approved':
        # Clinicians must access using patient_id
        if not patient_id:
            return redirect('clinician_dashboard')  # or show an error
        patient = get_object_or_404(Patient, id=patient_id)
    else:
        return redirect('home')  # or raise permission denied

    # You can now fetch the latest results for this patient
    # Replace the below line with actual result fetching logic
    context = {
        'patient': patient,
        # 'results': latest_results,
    }
    return render(request, 'patients/results.html', context)

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
            print(" User created:", user)
            print(" Role:", user.role)

            # Optional: Create patient profile if required
            Patients.objects.create(user=user)

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
