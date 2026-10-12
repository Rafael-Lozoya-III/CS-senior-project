
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.home,
        name="home",
    ),

    path(
        "accounts/login/",
        LoginView.as_view(
            template_name="accounts/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),

    path(
        "accounts/logout/",
        LogoutView.as_view(next_page="login"),
        name="logout",
    ),

    path(
        "accounts/signup/",
        views.signup,
        name="signup",
    ),

    path(
        "profile/",
        views.profile,
        name="profile",
    ),

    path(
        "profile/edit/",
        views.edit_profile,
        name="edit_profile",
    ),

    path(
        "professor/classes/",
        views.professor_classes,
        name="professor_classes",
    ),

    path(
        "professor/classes/create/",
        views.create_class,
        name="create_class",
    ),

    path(
        "discover/",
        views.discover,
        name="discover",
    ),

    path(
        "my-teams/",
        views.my_teams,
        name="my_teams",
    ),

    path(
        "projects/create/",
        views.create_project,
        name="create_project",
    ),

    path(
        "projects/applications/<int:application_id>/review/",
        views.review_project_application,
        name="review_project_application",
    ),

    path(
        "projects/<int:project_id>/apply/",
        views.apply_to_project,
        name="apply_to_project",
    ),

    path(
        "projects/<int:project_id>/",
        views.project_detail,
        name="project_detail",
    ),
]
