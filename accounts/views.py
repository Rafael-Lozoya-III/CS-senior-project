from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect,render

from .forms import StudentProfileForm
from .models import StudentProfile


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
    projects = [
        {
            "id": 1,
            "title": "AI Study Assistant",
            "course": "CSCI 4390",
            "description": "Build an AI-powered study assistant for college students.",
            "skills": ["Python", "AI", "Django"],
            "members": 3,
            "max_members": 4,
        },
        {
            "id": 2,
            "title": "Campus Marketplace",
            "course": "CSCI 4390",
            "description": "Create a marketplace where students can buy and sell items on campus.",
            "skills": ["Django", "HTML", "CSS"],
            "members": 2,
            "max_members": 4,
        },
        {
            "id": 3,
            "title": "Fitness Tracker",
            "course": "CSCI 4390",
            "description": "Develop an application for tracking workouts and fitness goals.",
            "skills": ["Java", "UI Design"],
            "members": 2,
            "max_members": 5,
        },
    ]

    return render(
        request,
        "accounts/discover.html",
        {"projects": projects},
    )

@login_required
def project_detail(request, project_id):
    projects = [
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

    project = next(
        (project for project in projects if project["id"] == project_id),
        None,
    )

    return render(
        request,
        "accounts/project_detail.html",
        {"project": project},
    )