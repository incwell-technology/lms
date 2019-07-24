from datetime import datetime,timedelta
from lms_user import models as lms_user_models
from django.contrib.auth.models import User
import re


def register_validation(request, context):
    pattern = '^[A-Za-z]+$'
    email = '^[a-zA-Z0-9_.+-]*@[a-zA-Z0-9-]*\.[a-zA-Z0-9-.]+$'
    if not re.match(pattern, request.POST['first_name']) or not re.match(pattern, request.POST['last_name']):
        context.update({'message':'First and Last name should not contain special characters'})
        return context 
    if len(request.POST['first_name'])<2 or len(request.POST['first_name'])>50 or len(request.POST['last_name'])<2 or len(request.POST['last_name'])>50:
        context.update({'message': 'First and Last name should not be less than 2 and greater than 50'})
        return context
    if not re.match(email, request.POST['email']):
        context.update({'message':'Invalid Email'})
        return context 
    try:
        existing_user = User.objects.get(email=request.POST['email'])
        context.update({'message': 'Could not register to LMS. Email Already exists'}) 
        return context
    except (User.DoesNotExist, Exception)  as e:
        print(e)
    try:
        phone = lms_user_models.LmsUser.objects.get(phone_number=request.POST['phone_number'])
        context.update({'message': 'Could not register to LMS. Phone number Already exists'})
        return context 
    except (lms_user_models.LmsUser.DoesNotExist, Exception) as e:   
        print(e)  
    if len(request.POST['phone_number']) > 10 or len(request.POST['phone_number']) < 10:
        context.update({'message': 'Invalid Phone Number.Phone number should be 10 digits'})
        return context
    if request.POST['date_of_birth'] > str(datetime.today()).split(' ')[0] or request.POST['date_of_birth'] < str(datetime.today() - timedelta(days=365*65)):
        context.update({'message': 'Invalid Date of Birth'})
        return context
    if request.POST['joined_date'] > str(datetime.today()).split(' ')[0]:
        context.update({'message': 'Invalid Joined Date'})
        return context
    return False


def leave_validation(request, context):
    if request.POST['from_date'] < str(datetime.today()).split(' ')[0] or request.POST['to_date'] < str(datetime.today()).split(' ')[0]:
        context.update({'message': 'Invalid Date'})
        return context
    if request.POST['from_date'] > request.POST['to_date']:
        context.update({'message': 'To Date is before From Date'})
        return context
    return False


def compensation_validtion(request,context):
    if int(request.POST['days']) > 100 or int(request.POST['days']) <= 0:
        context.update({'message': 'Invalid Number of days'})
        return context
    return False
