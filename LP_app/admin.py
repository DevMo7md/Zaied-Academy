from django.contrib import admin
from .models import *
# Register your models here.
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

CustomUser = get_user_model()

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # يمكنك تخصيص الحقول التي تظهر في واجهة الإدارة هنا
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'session_token')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

# تسجيل النموذج في واجهة الإدارة
admin.site.register(CustomUser, CustomUserAdmin)

admin.site.register(Lesson)
admin.site.register(Category)
admin.site.register(Student)
admin.site.register(Pdfs)
admin.site.register(Grade)
admin.site.register(MonthlySubscription)
admin.site.register(EmailVerification)