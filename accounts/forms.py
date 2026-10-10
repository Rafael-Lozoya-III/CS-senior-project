from django import forms
from boards.models import Class
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import StudentProfile, Skill, Interest



class StudentProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)

    interests = forms.ModelMultipleChoiceField(
        queryset=Interest.objects.all().order_by("name"),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = StudentProfile
        fields = ["grade_level", "experience", "interests"]
        labels = {
            "experience": "About Me",
        }
        widgets = {
            "experience": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Tell others about yourself...",
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

        self.user = user
        self.fields["first_name"].initial = user.first_name
        self.fields["last_name"].initial = user.last_name

        self.skill_fields = []

        for skill in Skill.objects.all().order_by("name"):
            field_name = f"skill_{skill.id}"

            self.fields[field_name] = forms.TypedChoiceField(
                label=skill.name,
                choices=[
                    ("", "Not selected"),
                    (1, "Beginner"),
                    (2, "Intermediate"),
                    (3, "Advanced"),
                ],
                coerce=int,
                empty_value=None,
                required=False,
            )

            self.skill_fields.append(self[field_name])

            if self.instance.pk:
                student_skill = self.instance.studentskill_set.filter(
                    skill=skill
                ).first()

                if student_skill:
                    self.fields[field_name].initial = student_skill.level

    def save(self, commit=True):
        profile = super().save(commit=False)

        if not commit:
            return profile

        self.user.first_name = self.cleaned_data["first_name"]
        self.user.last_name = self.cleaned_data["last_name"]
        self.user.save()

        profile.save()
        profile.interests.set(self.cleaned_data["interests"])

        for skill in Skill.objects.all():
            field_name = f"skill_{skill.id}"
            level = self.cleaned_data.get(field_name)

            if level is None:
                profile.studentskill_set.filter(skill=skill).delete()
            else:
                profile.studentskill_set.update_or_create(
                    skill=skill,
                    defaults={"level": level},
                )

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

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Example: CS 4390 - Senior Project",
            }),
            "description": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Describe your class...",
            }),
        }

    def clean_name(self):
        name = self.cleaned_data["name"]

        if Class.objects.filter(slug=slugify(name)).exists():
            raise forms.ValidationError(
                "A class with this name already exists."
            )

        return name