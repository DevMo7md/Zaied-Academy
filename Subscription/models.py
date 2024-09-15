from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, datetime
import pytz
from django.utils import timezone

class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.end_date is None:
            if self.start_date is None:
                self.start_date = timezone.now()  # استخدم timezone.now()
            self.end_date = self.start_date + timedelta(days=30)
        super().save(*args, **kwargs)

    def is_active(self):
        return self.end_date and self.end_date >= timezone.now()+ timedelta(hours=2)    # استخدم timezone.now()

    def __str__(self):
        return f"{self.user.username}'s subscription"







class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    paymob_order_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id}"


