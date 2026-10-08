from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render
from django.contrib.auth import login
from django.db import transaction

from .forms import StudentProfileForm, StudentSignUpForm
from .models import StudentProfile

TEMP_PROJECTS = [
    {
        "id": 1,
        "title": "AI Study Assistant",
        "course": "CSCI 4390",
        "description": "Build an AI-powered study assistant for college students.",
        "skills": ["Python", "AI", "Django"],
        "members": ["Alex R.", "Maria S.", "Jordan G."],
        "max_members": 4,
    },
    {
        "id": 2,
        "title": "Campus Marketplace",
        "course": "CSCI 4390",
        "description": "Create a marketplace where students can buy and sell items on campus.",
        "skills": ["Django", "HTML", "CSS"],
        "members": ["Chris M.", "Taylor B."],
        "max_members": 4,
    },
    {
        "id": 3,
        "title": "Fitness Tracker",
        "course": "CSCI 4390",
        "description": "Develop an application for tracking workouts and fitness goals.",
        "skills": ["Java", "UI Design"],
        "members": ["Sam P.", "Jamie L."],
        "max_members": 5,
    },
]

@login_required
def profile(request):
    student_profile = StudentProfile.objects.get(user=request.user)

    return render(
        request,
        "accounts/profile.html",
        {"student_profile": student_profile},
    )

@login_required
def edit_profile(request):
    student_profile = StudentProfile.objects.get(user=request.user)

    if request.method == "POST":
        form = StudentProfileForm(
            request.POST,
            instance=student_profile,
            user=request.user,
        )

        if form.is_valid():
            form.save()
            return redirect("profile")

    else:
        form = StudentProfileForm(
            instance=student_profile,
            user=request.user,
        )

    return render(
        request,
        "accounts/edit_profile.html",
        {"form": form},
    )

@login_required
def discover(request):
    return render(
        request,
        "accounts/discover.html",
        {"projects": TEMP_PROJECTS},
    )

@login_required
def project_detail(request, project_id):
    project = next(
        (project for project in TEMP_PROJECTS if project["id"] == project_id),
        None,
    )

    if project is None:
        raise Http404("Project not found.")

    return render(
        request,
        "accounts/project_detail.html",
        {"project": project},
    )

def signup(request):
    if request.user.is_authenticated:
        return redirect("discover")

    if request.method == "POST":
        form = StudentSignUpForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                user = form.save()

            login(request, user)
            return redirect("discover")
    else:
        form = StudentSignUpForm()

    return render(request, "accounts/signup.html", {"form": form})