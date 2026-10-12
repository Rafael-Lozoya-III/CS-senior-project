
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from boards.models import Class

from .forms import (
    StudentProfileForm,
    StudentSignUpForm,
    ClassForm,
    ProjectForm,
)
from .models import StudentProfile, Project, ProjectApplication


@login_required
def profile(request):
    if not StudentProfile.objects.filter(user=request.user).exists():
        raise PermissionDenied

    student_profile = StudentProfile.objects.get(user=request.user)

    return render(
        request,
        "accounts/profile.html",
        {"student_profile": student_profile},
    )


@login_required
def edit_profile(request):
    if not StudentProfile.objects.filter(user=request.user).exists():
        raise PermissionDenied

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
    projects = Project.objects.select_related(
        "creator",
        "class_group",
    ).order_by("-created_at")

    return render(
        request,
        "accounts/discover.html",
        {"projects": projects},
    )


@login_required
def my_teams(request):
    if not StudentProfile.objects.filter(user=request.user).exists():
        raise PermissionDenied

    created_projects = Project.objects.filter(
        creator=request.user
    ).select_related(
        "class_group"
    ).order_by("-created_at")

    joined_projects = Project.objects.filter(
        applications__applicant=request.user,
        applications__status="accepted",
    ).select_related(
        "creator",
        "class_group",
    ).distinct().order_by("-created_at")

    return render(
        request,
        "accounts/my_teams.html",
        {
            "created_projects": created_projects,
            "joined_projects": joined_projects,
        },
    )


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("creator", "class_group"),
        id=project_id,
    )

    applications = []

    if project.creator_id == request.user.id:
        applications = project.applications.filter(
            status="pending"
        ).select_related("applicant")

    accepted_members = project.applications.filter(
        status="accepted"
    ).select_related("applicant")

    member_count = accepted_members.count() + 1

    user_application = None

    if project.creator_id != request.user.id:
        user_application = project.applications.filter(
            applicant=request.user
        ).first()

    return render(
        request,
        "accounts/project_detail.html",
        {
            "project": project,
            "applications": applications,
            "accepted_members": accepted_members,
            "member_count": member_count,
            "user_application": user_application,
        },
    )


def signup(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = StudentSignUpForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                user = form.save()

            login(request, user)
            return redirect("discover")
    else:
        form = StudentSignUpForm()

    return render(
        request,
        "accounts/signup.html",
        {"form": form},
    )


@login_required
def professor_classes(request):
    if not hasattr(request.user, "teacherprofile"):
        raise PermissionDenied

    classes = Class.objects.filter(
        teacher=request.user
    ).prefetch_related("members")

    return render(
        request,
        "accounts/professor_classes.html",
        {"classes": classes},
    )


@login_required
def home(request):
    if hasattr(request.user, "teacherprofile"):
        return redirect("professor_classes")

    return redirect("discover")


@login_required
def create_class(request):
    if not hasattr(request.user, "teacherprofile"):
        raise PermissionDenied

    if request.method == "POST":
        form = ClassForm(request.POST)

        if form.is_valid():
            new_class = form.save(commit=False)
            new_class.teacher = request.user
            new_class.save()

            return redirect("professor_classes")
    else:
        form = ClassForm()

    return render(
        request,
        "accounts/create_class.html",
        {"form": form},
    )


@login_required
def create_project(request):
    if not StudentProfile.objects.filter(user=request.user).exists():
        raise PermissionDenied

    if request.method == "POST":
        form = ProjectForm(request.POST, user=request.user)

        if form.is_valid():
            project = form.save(commit=False)
            project.creator = request.user
            project.save()

            return redirect("discover")
    else:
        form = ProjectForm(user=request.user)

    return render(
        request,
        "accounts/create_project.html",
        {"form": form},
    )


@login_required
@require_POST
def apply_to_project(request, project_id):
    if not StudentProfile.objects.filter(user=request.user).exists():
        raise PermissionDenied

    project = get_object_or_404(Project, id=project_id)

    if project.creator_id == request.user.id:
        messages.error(
            request,
            "You cannot apply to your own project."
        )
        return redirect("project_detail", project_id=project.id)

    existing_application = ProjectApplication.objects.filter(
        project=project,
        applicant=request.user,
    ).first()

    if existing_application:
        messages.info(
            request,
            "You have already applied to this project."
        )
        return redirect("project_detail", project_id=project.id)

    member_count = (
        project.applications.filter(status="accepted").count() + 1
    )

    if member_count >= project.max_members:
        messages.error(
            request,
            "This project is already full."
        )
        return redirect("project_detail", project_id=project.id)

    if project.class_group and not project.class_group.members.filter(
        id=request.user.id
    ).exists():
        messages.error(
            request,
            "You must belong to this class to apply."
        )
        return redirect("project_detail", project_id=project.id)

    try:
        with transaction.atomic():
            ProjectApplication.objects.create(
                project=project,
                applicant=request.user,
            )
    except IntegrityError:
        messages.info(
            request,
            "You have already applied to this project."
        )
        return redirect("project_detail", project_id=project.id)

    messages.success(
        request,
        "Application submitted successfully!"
    )

    return redirect("project_detail", project_id=project.id)


@login_required
@require_POST
def review_project_application(request, application_id):
    decision = request.POST.get("decision")

    if decision not in ("accept", "reject"):
        messages.error(request, "Invalid decision.")
        return redirect("discover")

    with transaction.atomic():
        application = get_object_or_404(
            ProjectApplication.objects.select_related("project"),
            id=application_id,
        )

        project = get_object_or_404(
            Project.objects.select_for_update(),
            id=application.project_id,
        )

        if project.creator_id != request.user.id:
            raise PermissionDenied

        if application.status != "pending":
            messages.error(
                request,
                "This application has already been reviewed."
            )
            return redirect("project_detail", project_id=project.id)

        if decision == "accept":
            member_count = (
                project.applications.filter(status="accepted").count() + 1
            )

            if member_count >= project.max_members:
                messages.error(
                    request,
                    "This project is already full."
                )
                return redirect("project_detail", project_id=project.id)

            application.status = "accepted"
            application.save(update_fields=["status"])

            messages.success(
                request,
                "Application accepted!"
            )

        elif decision == "reject":
            application.status = "rejected"
            application.save(update_fields=["status"])

            messages.success(
                request,
                "Application rejected."
            )

    return redirect("project_detail", project_id=project.id)
