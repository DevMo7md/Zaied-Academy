from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Lesson)
admin.site.register(Category)
admin.site.register(Student)
admin.site.register(Pdfs)
admin.site.register(Grade)
admin.site.register(MonthlySubscription)
admin.site.register(EmailVerification)