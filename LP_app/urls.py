from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('home/', views.home, name='home'),
    path('lessons/<str:foo>/', views.lesson, name='lessons'),
    path('pdfs/', views.pdfs, name='pdfs'),
    path('video/<int:pk>/', views.video, name='video'),
    path('profile/<int:pk>/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('edit-pw/pass/', views.edit_ps, name='update_ps'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/get-subscription-stats/', views.get_and_update_subscription_stats, name='get_and_update_subscription_stats'),
    path('stat-dashboard/', views.stat_dashboard, name='stat_dashboard'),
    path('edit-lesson/<int:pk>/', views.edit_lesson, name='edit_lesson'),
    path('delete_lesson/<int:pk>/', views.delete_lesson, name='delete_lesson'),
    path('edit-pdf/<int:pk>/', views.edit_pdf, name='edit_pdf'),
    path('delete-pdf/<int:pk>/', views.delete_pdf, name='delete_pdf'),
    path('teacher-video/', views.teacher_video, name='teacher_video'),
    path('teacher-pdf/', views.teacher_pdfs, name='teacher_pdf'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:code>/', views.reset_password, name='reset_password'),
    path('student-teacher/', views.student_teacher, name='student_teacher'),
    path('update-profile-picture/<int:pk>/', views.update_profile_picture, name='update_profile_picture'),


]
