from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from .models import User
from .forms import CustomUserCreationForm

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

@login_required
def role_based_dashboard_redirect(request):
    if request.user.role == 'patient':
        return redirect('patient_dashboard')
    elif request.user.role == 'clinician':
        return redirect('clinician_dashboard')
    else:
        return redirect('/admin/')

@login_required
def patient_dashboard(request):
    return render(request, 'accounts/patient_dashboard.html')

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
            login(request, user)
            if user.role == 'patient':
                return redirect('patient_dashboard')
            elif user.role == 'clinician':
                return redirect('clinician_dashboard')
            else:
                return redirect('/admin/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', {'form': form})


# Create your views here.
