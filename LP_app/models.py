from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.utils import timezone
import uuid
from django.conf import settings

# Create your models here.
# models.py

class CustomUser(AbstractUser):
    session_token = models.CharField(max_length=100, blank=True, null=True)


class EmailVerification(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False, null=True, blank=True)  # لتتبع ما إذا تم استخدام الرمز أم لا
    
class Grade(models.Model):
    grade = models.CharField(max_length=50, null=True, blank=True)

    def __str__ (self):
        return self.grade

class Category(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='cat_images', null=True, blank=False)
    
    def __str__(self):
        return self.name

class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    second_name = models.CharField(max_length=255, null=True, blank=True)
    third_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    phone_num = models.CharField(max_length=20, null=True, blank=True)
    dad_num = models.CharField(max_length=255, null=True, blank=True)
    mom_num = models.CharField(max_length=255, null=True, blank=True)
    school = models.CharField(max_length=255, null=True, blank=True)
    dad_job = models.CharField(max_length=255, null=True, blank=True)
    government = models.CharField(max_length=255, null=True, blank=True)
    alsaf = models.ForeignKey(Grade ,on_delete=models.CASCADE ,null=True, blank=True)
    photo = models.ImageField(upload_to='student_photos', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    subscription_active = models.BooleanField(default=False)
    subscription_expiry = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return f'{self.first_name} {self.last_name} - username: {self.user.username}'



class Lesson(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True)
    discrebtion = models.TextField(null=True, blank=True)
    lesson = models.FileField(upload_to='lessons', null=True, blank=True)
    processed_video = models.FileField(upload_to='processed_videos/', blank=True, null=True)
    bdf = models.FileField(upload_to='bdfs', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    thumnale_image = models.ImageField(upload_to='thumnales', null=True, blank=True)
    added_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    views = models.PositiveIntegerField(default=0)  # حقل عدد المشاهدات
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title

class MonthlySubscription(models.Model):
    month = models.CharField(max_length=50, null=True, blank=True)  # تعديل نوع الحقل ليكون CharField
    new_subscribers = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.month} - {self.new_subscribers} subscribers"

class Pdfs(models.Model):
    name = models.CharField(max_length=100)
    pdf = models.FileField(upload_to='pdfs')
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='pdf_thumnale', null=True, blank=True)

    def __str__(self):
        return f' pdf: {self.name}'