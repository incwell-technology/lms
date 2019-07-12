from lms_user.models import LmsUser
from django.contrib.auth.models import User


def register_django_user(request, **kwargs):
    try:
        user = User.objects.create(username=request.POST['username'],
                                   email=request.POST['email'], first_name=request.POST['first_name'],
                                   last_name=request.POST['last_name'])
        user.set_password(request.POST['password'])
        user.save()
        return True

    except Exception as e:
        print(e)
        return False


def register_lms_user(**kwargs):
    if kwargs:
        try:
            detail = kwargs['user_details']
            LmsUser.objects.create(user=detail['user'], department=detail['department'],
                                   leave_issuer=detail['leave_issuer'], phone_number=detail['phone_number'],
                                   date_of_birth=detail['date_of_birth'], joined_date=detail['joined_date'])
            return True
        except Exception as e:
            print(e)
            return False
    return False
