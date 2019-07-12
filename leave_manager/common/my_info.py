from lms_user.models import LmsUser


def get_lms_user(user):
    user_detail = {}
    try:
        lms_user = LmsUser.objects.get(user=user)
        try:
            image_url = lms_user.image.url.split('/static/')[1]
        except Exception as e:
            print(e)
            image_url = 'lms_user/images/photograph.png'
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

    except Exception as e:
        print(e)
        return False


def get_user_photo_for_edit(id=id):
    user_detail = {}
    try:
        lms_user = LmsUser.objects.get(id=id)
        try:
            image_url = lms_user.image.url.split('/static/')[1]
        except Exception as e:
            image_url = 'lms_user/images/photograph.png'
        user_detail.update({
            'image':image_url
        })

        return user_detail
    except Exception as e:
        return False
    