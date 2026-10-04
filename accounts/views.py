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