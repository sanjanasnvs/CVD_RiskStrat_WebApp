from django import forms
from .models import Users 
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    biological_sex = forms.ChoiceField(
        choices=[('Male', 'Male'), ('Female', 'Female')],
        label='Biological Sex',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = Users
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'patient'
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
        return user
