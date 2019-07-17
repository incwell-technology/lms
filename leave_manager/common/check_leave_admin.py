from lms_user.models import LmsUser


def is_leave_issuer(user):
    hod = LmsUser.objects.filter(department__head_of_department=user).exists()
    leave_issuer = LmsUser.objects.filter(leave_issuer=user).exists()
    if hod or leave_issuer:
        return True
    else:
        return False