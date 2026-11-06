import calendar
from datetime import date
from django.db import transaction
from django.utils import timezone
from .models import RecurringIncome, Transaction

def process_recurring(user=None):
    today = timezone.localdate()
    schedules = RecurringIncome.objects.filter(active=True, start_date__lte=today)
    if user is not None: schedules = schedules.filter(user=user)
    created = 0
    for schedule in schedules:
        year, month = schedule.start_date.year, schedule.start_date.month
        while (year, month) <= (today.year, today.month):
            day = min(schedule.start_date.day, calendar.monthrange(year, month)[1])
            occurrence = date(year, month, day)
            if schedule.start_date <= occurrence <= today:
                with transaction.atomic():
                    _, was_created = Transaction.objects.get_or_create(recurring=schedule, occurrence=occurrence, defaults={'user':schedule.user,'kind':Transaction.INCOME,'title':schedule.name,'amount':schedule.amount,'date':occurrence})
                created += int(was_created)
            year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return created
