from datetime import datetime,timedelta
from lms_user import models as lms_user_models
from django.contrib.auth.models import User
import re

def validation(request):
    has_data = 0
    for d in request.data:
        if d == "first_name":
            has_data += 1
        if d == "last_name":  
            has_data += 1
        if d == "username":  
            has_data += 1
        if d == "email":  
            has_data += 1
        if d == "department":  
            has_data += 1
        if d == "date_of_birth":  
            has_data += 1
        if d == "joined_date":  
            has_data += 1
        if d == "password":  
            has_data += 1
    if has_data < 8:
        return False
    else:
        return True

def register_validation(request):
    pattern = '^[A-Za-z]+$'
    email = '^[a-zA-Z0-9_.+-]*@[a-zA-Z0-9-]*\.[a-zA-Z0-9-.]+$'
    if not re.match(pattern, request.data['first_name']) or not re.match(pattern, request.data['last_name']):
        message='First and Last name should not contain special characters'
        return message 
    if len(request.data['first_name'])<2 or len(request.data['first_name'])>50 or len(request.data['last_name'])<2 or len(request.data['last_name'])>50:
        message= 'First and Last name should not be less than 2 and greater than 50'
        return message
    if not re.match(email, request.data['email']):
        message='Invalid Email'
        return message 
    try:
        existing_user = User.objects.get(email=request.data['email'])
        print(existing_user)
        message= 'Could register to LMS. Email Already exists' 
        return message
    except (User.DoesNotExist, Exception)  as e:
        print(e)
    try:
        phone = lms_user_models.LmsUser.objects.get(phone_number=request.data['phone_number'])
        message= 'Could register to LMS. Phone number Already exists'
        return message 
    except (lms_user_models.LmsUser.DoesNotExist, Exception) as e:   
        print(e)  
    if len(request.data['phone_number']) > 10 or len(request.data['phone_number']) < 10:
        message= 'Invalid Phone Number.Phone number should be 10 digits long'
        return message
    if request.data['date_of_birth'] > str(datetime.today()) or request.data['date_of_birth'] < str(datetime.today() - timedelta(days=365*65)):
        message= 'Invalid Date of Birth'
        return message
    if request.data['joined_date'] > str(datetime.today()):
        message= 'Invalid Joined Date'
        return message
    if len(request.data['username']) >30  or len(request.data['username']) <5:
        message = 'Invalid Username'
        return message
    return False


def leave_validation(request):
    if request.data['from_date'] < str(datetime.today()).split(' ')[0] or request.data['to_date'] < str(datetime.today()).split(' ')[0]:
        message= 'Invalid Date'
        return message
    if request.data['from_date'] > request.data['to_date']:
        message= 'To Date is before From Date'
        return message
    return False


def compensation_validtion(request):
    if int(request.data['days']) > 100 or int(request.data['days']) <= 0:
        message= 'Invalid Number of days'
        return message
    return False
