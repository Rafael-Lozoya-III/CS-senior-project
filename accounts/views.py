from django.contrib.auth.decorators import login_required

from django.shortcuts import render

from .models import StudentProfile


@login_required
def profile(request):
    student_profile = StudentProfile.objects.get(user=request.user)

    return render(
        request,
        "accounts/profile.html",
        {"student_profile": student_profile},
    )