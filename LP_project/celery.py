from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# تعيين متغير البيئة لتحديد إعدادات Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LP_project.settings')

app = Celery('LP_project')

# تحميل إعدادات Celery من إعدادات Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# تحميل المهام من التطبيقات المسجلة
app.autodiscover_tasks()
