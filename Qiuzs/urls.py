from django.urls import path
from . import views

urlpatterns = [
    path('quiz-home/<str:foo>/', views.take_quiz_home, name='take_quiz_home'),
    path('quiz/<int:pk>/', views.take_quiz, name='take_quiz'),
    path('quiz-results/<int:pk>', views.quiz_results, name='quiz_results'),
    path('quizs-home/', views.quizs_home, name='quizs_home'),
    path('teacher-quiz/', views.teacher_quiz, name='teacher_quiz'),
    path('edit-quiz/<int:pk>/', views.edit_quiz, name='edit_quiz'),
    path('delete-quiz/<int:pk>/', views.delete_quiz, name='delete_quiz'),
    path('edit-choice/<int:pk>/', views.edit_choice, name='edit_choice'),
]
