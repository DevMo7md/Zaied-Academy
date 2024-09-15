from django.db import models
from django.contrib.auth.models import User
from LP_app.models import *
# Create your models here.

class Question(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, null=True, blank=True)
    text = models.CharField(max_length=255)  # نص السؤال
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)  # نص الاختيار
    is_correct = models.BooleanField(default=False)  # يشير إذا كان الاختيار صحيحًا

    def __str__(self):
        return f"{self.question.text} - {self.text}"

class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ربط المستخدم
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.question.text} - {self.selected_choice.text}"
