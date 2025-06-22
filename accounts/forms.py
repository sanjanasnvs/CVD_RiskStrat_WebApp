from django import forms
from .models import Users, Patients
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    sex = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female')], required=True)

    class Meta:
        model = Users
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'patient'
        if commit:
            user.save()

            # 🛡️ Check if patient already exists before creating
            if not hasattr(user, 'patients'):
                Patients.objects.create(user=user, sex=self.cleaned_data['sex'])
            else:
                # Optional update in case sex wasn't set
                user.patients.sex = self.cleaned_data['sex']
                user.patients.save()

        return user
