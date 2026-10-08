from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import StudentProfile


class StudentProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)

    class Meta:
        model = StudentProfile
        fields = ["grade_level", "experience"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

        self.user = user
        self.fields["first_name"].initial = user.first_name
        self.fields["last_name"].initial = user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)

        self.user.first_name = self.cleaned_data["first_name"]
        self.user.last_name = self.cleaned_data["last_name"]

        if commit:
            self.user.save()
            profile.save()

        return profile

class StudentSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField(required=True)
    grade_level = forms.ChoiceField(
        choices=StudentProfile.GRADE_LEVELS
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "grade_level",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if not email.endswith("@utrgv.edu"):
            raise forms.ValidationError(
                    "Please use your UTRGV school email."
            )
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )
        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

            StudentProfile.objects.create(
                user=user,
                grade_level=self.cleaned_data["grade_level"],
            )

        return user