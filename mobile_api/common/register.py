from django.contrib.auth.models import User

def register_django_user(request, **kwargs):
    try:
        user = User.objects.create(username=request.data['username'],
                                   email=request.data['email'], first_name=request.data['first_name'],
                                   last_name=request.data['last_name'])
        user.set_password(request.data['password'])
        user.save()
        return True

    except Exception as e:
        print(e)
        return False
