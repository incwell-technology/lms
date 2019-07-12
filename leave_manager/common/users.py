from lms_user.models import LmsUser
from datetime import datetime, timedelta
from django.db.models import Q
from calendar import monthrange

def get_lms_users():
    users = []
    for lms_user in LmsUser.objects.all():
        users.append({
            'id':lms_user.user.id,
            'full_name': lms_user.user.get_full_name(),
            'phone_number': lms_user.phone_number,
            'email': lms_user.user.email,
            'department': lms_user.department.department,
            'leave_issuer': lms_user.leave_issuer.get_full_name(),
            'leave_issuer_id':lms_user.leave_issuer.id
        })
    return users


def get_birthday_today():
    today = datetime.today()
    users = []
    upcoming_bday_users = []
    for user in LmsUser.objects.filter(date_of_birth__day=today.day, date_of_birth__month=today.month):
        try:
            image_url = user.image.url.split('/static/')[1]
        except Exception as e:
            print(e)
            image_url = 'lms_user/images/photograph.png'
        users.append({
            'full_name': user.user.get_full_name(),
            'image': image_url,
            'department': user.department.department
        })
    date_after_5_days = today+timedelta(6)
    month = []
    day = []
    for date in range(0,5):
        day.append((today+timedelta(date)).day)
        month.append((today+timedelta(date)).month)

    for user in LmsUser.objects.filter(Q(date_of_birth__month__lte=date_after_5_days.month) and Q(date_of_birth__month__gte=today.month), Q(date_of_birth__day__lte=date_after_5_days.day) and Q(date_of_birth__day__gte=today.day)):
        try:
            image_url = user.image.url.split('/static/')[1]
        except Exception as e:
            print(e)
            image_url = 'lms_user/images/photograph.png'
        for date in range(0,5):
            if user.date_of_birth.month == month[date] and user.date_of_birth.day == day[date]:
                upcoming_bday_users.append({
                    'full_name': user.user.get_full_name(),
                    'department': user.department.department,
                    'dob':user.date_of_birth,
                    'remaining': date
                    })
    all_data = {
        'users':users,
        'upcoming':upcoming_bday_users
        }
    return all_data
