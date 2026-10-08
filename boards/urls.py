from django.urls import path
from . import views

urlpatterns = [
    path('', views.board_list, name='board_list'),
    path('class/<slug:slug>/', views.class_detail, name='class_detail'),
    path('class/<slug:slug>/new/', views.new_thread,
         {'scope': 'class'}, name='new_class_thread'),
    path('class/<slug:slug>/team/<slug:team_slug>/',
         views.team_detail, name='team_detail'),
    path('class/<slug:slug>/team/<slug:team_slug>/new/',
         views.new_thread, {'scope': 'team'}, name='new_team_thread'),
    path('thread/<slug:slug>/', views.thread_detail, name='thread_detail'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
]