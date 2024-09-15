from django.core.management.base import BaseCommand
from LP_app.models import MonthlyStatistics
from django.utils import timezone
from datetime import datetime

class Command(BaseCommand):
    help = 'Update statistics for the new month'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        current_year = now.year
        current_month = now.month

        # Check if statistics for this month already exist
        if MonthlyStatistics.objects.filter(month__year=current_year, month__month=current_month).exists():
            self.stdout.write(self.style.SUCCESS('Statistics for this month already exist.'))
            return

        # Add new entry for the current month with default subscribers count (0 or other value)
        MonthlyStatistics.objects.create(
            month=datetime(current_year, current_month, 1),
            new_subscribers=0  # You can update this with real data later
        )
        self.stdout.write(self.style.SUCCESS('Statistics updated successfully.'))