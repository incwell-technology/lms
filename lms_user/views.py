from datetime import datetime
from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth import forms as auth_forms
from lms_user.models import Department
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from lms_user.common.register import register_django_user, register_lms_user
from leave_manager.common.routes import get_formatted_routes, get_routes, is_leave_issuer
from leave_manager.common.leave_manager import get_all_leaves_unseen 
from lms_user.tokens import password_reset_token
from lms_user.common import send_mail as send_mail
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
import jwt
import yaml
# from lms_user.login import nothing


# Create your views here.

def user_login(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return render(request, 'lms_user/login.html', {'message': 'Login', 'title': 'LMS | Login'})
        else:
            return HttpResponseRedirect(reverse('user-index'))

    else:
        user = authenticate(request, username=request.POST["username"], password=request.POST["password"])
        if user is None:
            return render(request, 'lms_user/login.html', {'message': 'Invalid Credentials'})
        else:
            login(request, user)
            return HttpResponseRedirect(reverse('user-index'))


def user_logout(request):
    if request.method == 'GET':
        print('logout get')
        return HttpResponseRedirect(reverse('user-index'))

    else:
        logout(request)
        print('logout post')
        return HttpResponseRedirect(reverse('user-login'))


def user_register(request):
    context = {
        'departments': Department.objects.all()
    }
    leaves = get_all_leaves_unseen()
    context.update({'leave_notify':leaves})
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))
    if not is_leave_issuer(request.user):
        return HttpResponseRedirect(reverse('leave_manager_dashboard'))
    routes = get_formatted_routes(get_routes(request.user), active_page='register user')
    context.update({'routes': routes})
    if request.method == 'GET':
        if not request.user.is_authenticated:
            url = reverse('user-login')
            return HttpResponseRedirect(url)
        return render(request, 'lms_user/register.html', context=context)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            url = reverse('user-login')
            return HttpResponseRedirect(url)
        else:
            try:
                existing_user = User.objects.get(email=request.POST['email'])
                context.update({'message': 'Could not register. Please contact Admin or try again later'})
                return render(request, 'lms_user/register.html', context=context)
            except (User.DoesNotExist, Exception) as e:
                print(e)
                try:    
                    if register_django_user(request):
                        user = User.objects.get(username=request.POST['username'])
                        department = Department.objects.get(id=int(request.POST['department']))
                        lms_user_details = {
                            'user': user,
                            'phone_number': request.POST['phone_number'],
                            'department': department,
                            'leave_issuer': department.head_of_department,
                            'date_of_birth': datetime.strptime(request.POST['date_of_birth'], '%Y-%m-%d'),
                            'joined_date': datetime.strptime(request.POST['joined_date'], '%Y-%m-%d')
                        }
                        if register_lms_user(user_details=lms_user_details):
                            return HttpResponseRedirect(reverse('user-index'))
                        else:
                            try:
                                user.delete()
                                context.update({'message': 'Could register to LMS. Please contact Admin or try again later'})
                                return render(request, 'lms_user/register.html', context=context)
                            except Exception as e:
                                print(e)
                                return render(request, 'lms_user/register.html', context=context)
                    else:
                        context.update({'message': 'Could register to Django. Please contact Admin or try again later'})
                        return render(request, 'lms_user/register.html', context=context)

                except (User.DoesNotExist, Department.DoesNotExist, Exception) as e:
                    print(e)
                    context.update({'message': 'Could not register. Please contact Admin or try again later'})
                    return render(request, 'lms_user/register.html', context=context)


def index(request):
    if not request.user.is_authenticated:
        url = reverse('user-login')
        return HttpResponseRedirect(url)
    print('Yay!!! I am logged in .....')
    return HttpResponseRedirect(reverse('leave_manager_dashboard'))


def change_password(request):
    context = {}
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))
    routes = get_formatted_routes(get_routes(request.user), active_page='change password')
    context.update({'routes': routes})
    if request.method == 'POST':
        form = auth_forms.PasswordChangeForm(request.user, request.POST)
        if form.is_valid() and send_mail.send_email(request,request.user,'Password Change'):
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return HttpResponseRedirect(reverse('leave_manager_dashboard'))
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form =  auth_forms.PasswordChangeForm(request.user)
    context.update({'form':form})
    return render(request, 'lms_user/changePassword.html', context=context)


def password_reset(request):
    context = {}
    if request.method == 'POST':
        form = auth_forms.PasswordResetForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(email = request.POST['email'])
            except (User.DoesNotExist, Exception):
                user = None
            if user and send_mail.send_email(request,user,'Password Reset'):
                return HttpResponseRedirect('password-reset/done')
            else:
                return render(request, 'lms_user/password_reset_fail.html')
    else:
        form = auth_forms.PasswordResetForm()
    context.update({'form':form})
    return render(request, 'lms_user/password_reset_form.html', context=context)


def password_reset_done(request, token):
    context = {}
    credentials = yaml.load(open('credentials.yaml'))
    try:
        decoded = jwt.decode(token, credentials['secret'], algorithms='HS256',options={'verify_exp': False})
        user = User.objects.get(email=decoded['email'])
        exp = decoded['expires']
    except Exception as e:
        print(e)
        user = None
    if user and exp > str(datetime.now()):
        validlink = True
        if request.method == 'POST':
            form = auth_forms.SetPasswordForm(user,request.POST)
            if form.is_valid() and send_mail.send_email(request,user,'Password Change'):
                form.save()
                return render(request,'lms_user/password_reset_complete.html',context=context)
        else:
            form = auth_forms.SetPasswordForm(user)
        context.update({'form':form})
        context.update({'validlink':validlink})
        return render(request,'lms_user/password_reset_confirm.html',context=context)
    else:   
        validlink =False
        context.update({'validlink':validlink})
        return render(request,'lms_user/password_reset_confirm.html',context=context)