from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views


urlpatterns = [
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
        name="logout"
    ),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("accounts/signup/", views.signup, name="signup"),
    path("discover/", views.discover, name="discover"),
    path(
        "projects/<int:project_id>/",
        views.project_detail,
        name="project_detail",
    ),
]