from lms_user import models as lms_user_models
from leave_manager import models as leave_manager_models

def get_image_url_mobile(user,request, image_for,holiday_id):
    image_url = ''
    try:
        if holiday_id:
            holiday = leave_manager_models.Holiday.objects.get(id=holiday_id)
        full_path = request.build_absolute_uri()
        path = full_path.split('/v1/')[0]
        try:
            if image_for == 'user':
                image_url = path + '/static' + user.image.url.split('/static')[1]
            else:
                image_url = path + '/static' + holiday.image.url.split('/static')[1]
        except Exception as e:
            print(e)
            if image_for == 'user':
                image_url = path + '/static/lms_user/images/photograph.png'
            else:
                image_url = path + '/static/lms_user/images/yay.png'
        return image_url
    except (lms_user_models.LmsUser.DoesNotExist ,leave_manager_models.Holiday.DoesNotExist):
        return False
    