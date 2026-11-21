from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_redirect, name='home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),

    # Core Pages matching UI Screens
    path('dashboard/', views.dashboard_view, name='dashboard'),      # Screen 4 (Aivance)
    path('chat/', views.chat_view, name='chat'),                    # Screen 1 (CareerWithinU)
    path('careers/', views.careers_view, name='careers'),            # Screen 3 (My Choices / Best Matches)
    path('careers/<slug:slug>/', views.career_detail_view, name='career_detail'),
    path('roadmap/', views.roadmap_view, name='roadmap'),            # Screen 2 (Ascento)
    path('roadmap/<slug:career_slug>/', views.roadmap_view, name='career_roadmap'),
    path('compare/', views.career_compare_view, name='career_compare'),
    path('profile/', views.profile_wizard_view, name='profile_wizard'),
    path('admin-portal/', views.admin_portal_view, name='admin_portal'),

    # APIs
    path('api/chat/', views.api_chat_message, name='api_chat_message'),
    path('api/milestone/update/', views.api_update_milestone, name='api_update_milestone'),
    path('api/career/save/', views.api_toggle_save_career, name='api_toggle_save_career'),
    path('api/cv/upload/', views.api_upload_cv, name='api_upload_cv'),
    path('api/interview/schedule/', views.api_schedule_interview, name='api_schedule_interview'),
]
