from django import forms
from .models import Users 
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    class Meta:
        model = Users
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'patient'
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
        return user
