from lms_user.models import LmsUser
from mobile_api.common.user_image import get_image_url_mobile
from datetime import datetime, timedelta
from django.db.models import Q


def get_lms_user_mobile(user, request):
    user_detail = {}
    try:
        lms_user = LmsUser.objects.get(user=user)
        image_url = get_image_url_mobile(lms_user.user,request,'user',None)
        user_detail.update({
            'full_name': lms_user.user.get_full_name(),
            'phone_number': lms_user.phone_number,
            'email': lms_user.user.email,
            'department': lms_user.department.department,
            'leave_issuer': lms_user.leave_issuer.get_full_name(),
            'image': image_url,
            'sick_leaves': lms_user.sick_leave,
            'annual_leaves': lms_user.annual_leave,
            'compensation_leaves': lms_user.compensation_leave,
            'date_of_birth': str(lms_user.date_of_birth),
            'joined_date': str(lms_user.joined_date),
            'id':lms_user.id
        })
        return user_detail

    except LmsUser.DoesNotExist:
        return False



def get_birthday_today(request):
    today = datetime.today()
    users = []
    upcoming_bday_users = []
    for user in LmsUser.objects.filter(date_of_birth__day=today.day, date_of_birth__month=today.month):
        image_url = get_image_url_mobile(user, request, 'user' ,None)
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
        image_url = get_image_url_mobile(user, request, 'user' ,None)
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