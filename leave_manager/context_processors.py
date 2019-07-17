from django.db.models import Q
from calendar import monthrange
from datetime import datetime, timedelta
from lms_user.models import LmsUser
from leave_manager.common import check_leave_admin

def get_birthday_notification(request):
    have_birthday = {}
    today = datetime.today()
    date_after_5_days = today+timedelta(6)
    month = []
    day = []
    for date in range(0,5):
        day.append((today+timedelta(date)).day)
        month.append((today+timedelta(date)).month)

    counter = 0
    for user in LmsUser.objects.filter(Q(date_of_birth__month__lte=date_after_5_days.month) and Q(date_of_birth__month__gte=today.month), Q(date_of_birth__day__lte=date_after_5_days.day) and Q(date_of_birth__day__gte=today.day)):
        for date in range(0,5):
            if user.date_of_birth.month == month[date] and user.date_of_birth.day == day[date]:
                counter+=1

    if counter > 0:
        have_birthday.update({'upcoming_birthday':counter})
    return have_birthday
