from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from .models import Users
from .forms import CustomUserCreationForm
from .models import *
from django.shortcuts import get_object_or_404


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.role == 'patient':
                return redirect('patient_dashboard')
            elif user.role == 'clinician':
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


@login_required
def assessment_view(request):
    # Get category from URL, default to first one
    category = request.GET.get('category', None)

    # Get all unique categories ordered by their logical sequence
    all_categories = list(CVD_risk_Questionnaire.objects.order_by('question_order').values_list('category', flat=True).distinct())

    # Default to first if not provided
    if not category:
        return redirect(f"{reverse('start_assessment')}?category={all_categories[0]}")

    # Get completed categories from session
    completed_categories = request.session.get('completed_categories', [])
    
    # Find previous and next categories for navigation
    try:
        current_index = all_categories.index(category)
        previous_category = all_categories[current_index - 1] if current_index > 0 else None
        next_category = all_categories[current_index + 1] if current_index + 1 < len(all_categories) else None    
    except ValueError:
        previous_category = None
        next_category = None

    # Load questions for this category
    questions = CVD_risk_Questionnaire.objects.filter(category=category).order_by('question_order')

    if request.method == 'POST':
        # Save responses
        all_valid = True
        for q in questions:
            key = f"question_{q.question_id}"
            value = request.POST.get(key)

            if not value and q.required:  # Check if required question is answered
                all_valid = False
                break

            if value:  # Skip unanswered optional questions
                CVD_risk_Responses.objects.update_or_create(
                    patient = Patients.objects.get(user=request.user)
                    patient=patient,
                    question=q,
                    defaults={'response': value}
                )

        if all_valid:
            # Mark this category as completed
            if category not in completed_categories:
                completed_categories.append(category)
                request.session['completed_categories'] = completed_categories
            
            # Go to next category or finish
            if next_category:
                return redirect(f"{reverse('start_assessment')}?category={next_category}")
            else:
                # Clear completed categories from session when assessment is complete
                request.session['completed_categories'] = []
                return redirect('patient_results')  # Redirect to results page
        else:
            # If validation fails, stay on current page with error message
            error_message = "Please answer all required questions."
            # Build question + options list
            question_data = []
            for q in questions:
                options = CVD_risk_QuestionResponseOptions.objects.filter(question=q)
                # Get saved response if any
                patient = Patients.objects.get(user=request.user)
                saved_response = CVD_risk_Responses.objects.filter(patient=patient, question=q).first()
                response_value = saved_response.response if saved_response else None
                question_data.append({
                    'question': q, 
                    'options': options,
                    'response': response_value
                })
            
            return render(request, 'assessment.html', {
                'category': category,
                'question_data': question_data,
                'all_categories': all_categories,
                'completed_categories': completed_categories,
                'previous_category': previous_category,
                'next_category': next_category,
                'error_message': error_message
            })

    # Build question + options list with any saved responses
    question_data = []
    for q in questions:
        options = CVD_risk_QuestionResponseOptions.objects.filter(question=q)
        # Get saved response if any
        patient = Patients.objects.get(user=request.user)
        saved_response = CVD_risk_Responses.objects.filter(patient=patient, question=q).first()
        response_value = saved_response.response if saved_response else None
        question_data.append({
            'question': q, 
            'options': options,
            'response': response_value
        })

    return render(request, 'assessment.html', {
        'category': category,
        'question_data': question_data,
        'all_categories': all_categories,
        'completed_categories': completed_categories,
        'previous_category': previous_category,
        'next_category': next_category
    })

def get_next_category(category_list, current):
    """Helper function to get the next category in the list"""
    try:
        idx = category_list.index(current)
        return category_list[idx + 1] if idx + 1 < len(category_list) else None
    except ValueError:
        return None
 
@login_required
def patient_results(request):
    # fetch latest result for the patient
    if request.user.role != 'patient':
        return redirect('home')
    return render(request, 'patients/results.html')

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
    return render(request, 'accounts/clinician_dashboard.html')

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
