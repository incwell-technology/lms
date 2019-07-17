from django.shortcuts import render
from mobile_api.common import user_info as user_info
from django.contrib.sessions.models import Session
from mobile_api.common.user_image import get_image_url_mobile
from django.http import JsonResponse
from datetime import datetime, timedelta, date
import json
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import  FormParser, MultiPartParser
from mobile_api.common import leave_manager
from leave_manager import models as leave_models
from lms_user import models as lms_user_models
from mobile_api import serializers as mobile_api_serializers
from leave_manager.common.check_leave_admin import is_leave_issuer
from leave_manager.common.leave_manager import get_all_leaves_unseen
from mobile_api.common.register import register_django_user
from leave_manager import common as leave_common
from lms_user.models import Department
from django.contrib.auth.models import User
from mobile_api.common.validation import  validation
import firebase_admin
from firebase_admin import messaging
from leave_manager.models import LeaveType
from mobile_api.common.fcm import fcm, subcription
from lms_user.common import send_mail as send_mail
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from lms_user.tokens import password_reset_token
from mobile_api import models as mobile_api_models
from mobile_api.common import user_info as mobile_user_info
import jwt
import yaml

credentials = yaml.load(open('credentials.yaml'))

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    try:
        json_to_dict = json.loads(request.body)
        user = authenticate(request, username=json_to_dict['username'], password=json_to_dict['password'])
        if user is None:
            return JsonResponse({"status":False,"error":"Invalid Credentials"})
        token, _ = Token.objects.get_or_create(user=user)
        lms_user = user_info.get_lms_user_mobile(user, request)
        try:
            lms_user_fcm = lms_user_models.LmsUser.objects.get(user=user)
            lms_user_fcm.fcm_token = request.data['fcm_token']
            lms_user_fcm.save()
            subcription(lms_user_fcm.fcm_token, "holiday")
        except (lms_user_models.LmsUser.DoesNotExist, Exception) as e:
            print(e)
        return JsonResponse({"status":True,"data":lms_user, 'token': token.key}, status=200)
    except Exception as e:
        print("err",e)
        return JsonResponse({}, status=500)


@csrf_exempt
@api_view(["GET"])
def holidays(request):
    try:
        holiday = leave_models.Holiday.objects.all()
        data = []
        for i in holiday:
            delta = i.from_date - date.today()
            image_url = get_image_url_mobile(None, request, 'holiday' ,i.id)
            if delta.days >= 0:
                data.append({
                    'id':i.id,
                    'title':i.title,
                    'date':i.from_date,
                    'days': delta.days,
                    'image': image_url
                })
            if delta.days == 0:
                fcm(None,i.title,"holiday")
        return JsonResponse({"status":True,"data":data}, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({}, status=500)

@csrf_exempt
@api_view(["GET"])
def birthday(request):
    today = datetime.today()
    users = {}
    try:
        birthday_today = user_info.get_birthday_today(request)['users']
        users.update({'birthdays': birthday_today})
        upcoming_bday = user_info.get_birthday_today(request)['upcoming']
        upcoming_bday_visible = False
        if is_leave_issuer(request.user):
            upcoming_bday_visible = True
            users.update({'upcoming_bday': upcoming_bday})
        users.update({'upcoming_bday_visible': upcoming_bday_visible})
        return JsonResponse({"status":True,"data":users}, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({}, status=500)


@csrf_exempt
@api_view(["GET"])
def leave(request):
    try:
        leave = leave_manager.get_leave_today_mobile(request)
        return JsonResponse({"status":True,"data":leave}, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({}, status=500)


@csrf_exempt
@api_view(["POST"])
def user_register(request):
    if is_leave_issuer(request.user):
        if request.method == 'POST':
            if validation(request):
                try:
                    existing_user = User.objects.get(email=request.data['email'])
                    return JsonResponse({'status':False,'message':'User with this email already exists'}, status=500) 
                except (User.DoesNotExist, Exception):
                    if register_django_user(request):
                        try:
                            user = User.objects.get(username=request.data['username'])
                            department = Department.objects.get(id=int(request.data['department']))
                        except (User.DoesNotExist, Department.DoesNotExist):
                            return JsonResponse({}, status=500) 
                        lms_user = {}
                        lms_user.update({
                            'user': user.pk,
                            'phone_number': request.data['phone_number'],
                            'department': department.pk,
                            'leave_issuer': department.head_of_department.pk,
                            'date_of_birth': request.data['date_of_birth'],
                            'joined_date': request.data['joined_date']
                        })
                        serializer = mobile_api_serializers.UserSerializer(data = lms_user)
                        if serializer.is_valid():
                            serializer.save()
                            lms_user = mobile_user_info.get_lms_user_mobile(user, request)
                            return JsonResponse({"status":True, "payload":lms_user}, status=201)
                        else:
                            try:
                                user.delete()
                                return JsonResponse({"status":False,"mesasge":"Couldn't register user"}, status=400)
                            except Exception as e:
                                print(e)
                                return JsonResponse({"status":False,"mesasge":"Couldn't delete registered user"}, status=400)

                    else:
                        return JsonResponse({"status":False,"mesasge":"User already exists"}, status=400)
            else:
                return JsonResponse({"status":False,"message":"All fields required"}, status=400)
    else:
        return JsonResponse({"status":False,"message":"You are not authorized to register user"}, status=403)


@csrf_exempt
@api_view(["GET"])
def users(request):
    data = []
    for user in lms_user_models.LmsUser.objects.all():
        generate_report_access = False
        if is_leave_issuer(user.user):
            generate_report_access = True
        image_url = get_image_url_mobile(user, request, 'user' ,None)
        data.append({
            "generate_report_access": generate_report_access,
            "full_name": user.user.get_full_name(),
            "email": user.user.email,
            "phone": user.phone_number,
            "department": user.department.department,
            "leave_issuer":user.leave_issuer.get_full_name(),
            "image":image_url
            })
    return JsonResponse({"status":True,"data":data}, status=200)
    

@csrf_exempt
@api_view(['POST'])
def create_leaves(request):
    if request.method == 'POST':
        try:
            if leave_manager.check_leave_applicability(request.user, request.data["type"]): 
                user = lms_user_models.LmsUser.objects.get(user=request.user)
                leave_type = LeaveType.objects.get(type=request.data["type"])
                leave_issuer = lms_user_models.LmsUser.objects.get(user=user.leave_issuer)
                leave_issuer_fcm = leave_issuer.fcm_token
                lms_user = {}
                lms_user.update({
                    "user":user.pk,
                    "type": leave_type.pk,
                    "from_date": request.data["from_date"],
                    "to_date": request.data["to_date"],
                    "reason": request.data["leave_reason"],
                    "half_day": request.data["half_day"]
                })
                serializer = mobile_api_serializers.LeaveSerializer(data = lms_user)
                if serializer.is_valid():
                    serializer.save()
                    fcm(leave_issuer_fcm,user,"leave_apply")
                    return JsonResponse({"status":True, "payload":lms_user}, status=200)
                else:
                    return JsonResponse({"status":False, "mesasge":"Invalid data"}, status=400)
            else:
                return JsonResponse({"status":False, "mesasge":"No leave available to apply"}, status=400)
        except (LeaveType.DoesNotExist , lms_user_models.LmsUser.DoesNotExist, Exception) as e:
            print(e)
            return JsonResponse({"status":False, "message":"Unable to apply"}, status=400)
    else:
        return JsonResponse({"status":False,"message":"Coudln't apply"}, status=400) 


@csrf_exempt
@api_view(["GET"])
def get_fcm_token(request):
    fcm_token = request.data['fcm_token']
    return fcm_token   


@csrf_exempt
@api_view(["GET"])
def get_leave_request(request):
    try:
        if is_leave_issuer(request.user):
            leave = leave_manager.get_leave_requests_mobile(request.user)
            return JsonResponse({"status":True,"data":leave}, status=200)
        else:
            return JsonResponse({"status":False,"message":"Not authorized to view this"}, status=500)
    except Exception as e:
        print(e)
        return JsonResponse({}, status=500)
        

@csrf_exempt
@api_view(["POST"])
def leave_approval_or_rejection(request, id):
    try:
        if not is_leave_issuer(request.user):
            return JsonResponse({"status":False, "message":"Not authorized to view this"}, status=400)
        leave = leave_models.Leave.objects.get(id=id)
        leave.notification = False
        leave.save()
        if request.method == 'POST':
            if leave.leave_pending == True:
                if request.data['leave_response'] == '2':
                    if leave_manager.reject_leave_request(request, id):
                        return JsonResponse({"status":True, "message": "Rejection Success"},status=200)
                    else:
                        return JsonResponse({"message":"Rejection Failed"},status=400)
                elif request.data['leave_response'] == '1':
                    if leave_manager.approve_leave_request(request, id):
                        return JsonResponse({"status":True,"message": "Approval Success"},status=200)
                    else:
                        return JsonResponse({"status":False, "message":"Approval Failed"},status=400)
            else:
                return JsonResponse({"message":"Already approved or rejected" },status= 200)
    except (leave_models.Leave.DoesNotExist, Exception) as e:
        print(e)
        return JsonResponse({},status= 500)


@csrf_exempt
@api_view(["POST"])
def compensation_leave(request):
    try:
        if request.method == 'POST':
            user = lms_user_models.LmsUser.objects.get(user=request.user)  
            leave_issuer = lms_user_models.LmsUser.objects.get(user=user.leave_issuer)
            leave_issuer_fcm = leave_issuer.fcm_token
            leave_details = {}
            leave_details.update({
                "user": user.pk,
                "reason": request.data['leave_reason'],
                "days":request.data['days']
            })
            serializer = mobile_api_serializers.CompensationSerializer(data = leave_details)
            if serializer.is_valid():
                serializer.save()
                fcm(leave_issuer_fcm,user,"compensation_apply")
                return JsonResponse({"status":True, "payload":leave_details}, status=200)
            else:
                print(serializer.errors)

                return JsonResponse({"status":False, "mesasge":"Invalid data"}, status=400)
        else:
            return JsonResponse({"staus":False, "message":"Couldn't apply for compenstation"}, status=500)
    except (lms_user_models.LmsUser.DoesNotExist,Exception) as e:
        print(e)
        return JsonResponse({}, status=500)


@csrf_exempt
@api_view(["GET"])
def get_compensation_request(request):
    try:
        if is_leave_issuer(request.user):
            leave = leave_manager.get_compensationLeave_requests_mobile(request.user)
            return JsonResponse({"status":True,"data":leave}, status=200)
        else:
            return JsonResponse({"status":False,"message":"Not authorized to view this"}, status=500)
    except Exception as e:
        print(e)
        return JsonResponse({}, status=500)
        

@csrf_exempt
@api_view(["POST"])
def compensation_approval_reject(request, id):
    try:
        if not is_leave_issuer(request.user):
            return JsonResponse({"status":False, "message":"Not authorized to view this"}, status=400)
        leave = leave_models.CompensationLeave.objects.get(id=id)
        leave.notification = False
        leave.save()
        if request.method == 'POST':
            if leave.leave_pending == True:
                if request.data['leave_response'] == '2':
                    if leave_manager.reject_compensationLeave_request(request, id):
                        return JsonResponse({"status":True, "message": "Rejection Success"},status=200)
                    else:
                        return JsonResponse({"message":"Rejection Failed"},status=400)
                elif request.data['leave_response'] == '1':
                    if leave_manager.approve_compensationLeave_request(request, id):
                        return JsonResponse({"status":True,"message": "Approval Success"},status=200)
                    else:
                        return JsonResponse({"status":False, "message":"Approval Failed"},status=400)
            else:
                return JsonResponse({"message":"Already approved or rejected" },status= 200)
    except (leave_models.CompensationLeave.DoesNotExist, Exception) as e:
        print(e)
        return JsonResponse({},status= 500)


@csrf_exempt
@api_view(['GET'])
def leaveHistory(request):
    try:
        context = []
        date_today = date.today()
        lms_user = lms_user_models.LmsUser.objects.get(user=request.user)
        data = leave_manager.get_own_leave_history_monthly(lms_user.id, date.month)
        compensation_data = leave_manager.get_own_compensationLeave_detail_monthly(lms_user.id)
        context.append({
            "date":date_today,
            "leave":data,
            "compensation_leave":compensation_data
        })
        return JsonResponse({"status":True, "payload":context},status=200)
    except (lms_user_models.LmsUser.DoesNotExist, Exception) as e:
        print(e)
        return JsonResponse({"status":False, "message":"Error"}, status=500)
        

@csrf_exempt
@api_view(["POST"])  
def generate_leave_report(request):
    context = {}
    if not is_leave_issuer(request.user):
        return JsonResponse({"status":False, "message":"Not authorized to view this"}, status=400)
    if request.method == "POST":
        from_date = datetime.strptime(request.data['from_date'], '%Y-%m-%d').date()
        to_date = datetime.strptime(request.data['to_date'], '%Y-%m-%d').date()
        leave_list = leave_manager.get_users_leaveDetailFor_searchEngine(request.user,from_date,to_date)
        if leave_list == {}:
            context.update({'reports':" "})            
        else:
            context.update({'reports':sorted(leave_list.items())})
        context.update({'from_date':from_date})
        context.update({'to_date':to_date})
        return JsonResponse({"status":True, "payload":context},status=200)
    else:
        return JsonResponse({"status":False, "message":"Error"}, status = 500)


@csrf_exempt
@api_view(['GET'])
def leave_report_details(request, id):
    try:
        context = {}
        leave_detail = []
        leaves = leave_models.Leave.objects.filter(user__user__id=id)
        lms_user = lms_user_models.LmsUser.objects.get(user__id=id)
        image_url = get_image_url_mobile(lms_user.user, request, 'user' ,None)
        for leave in leaves:
            leave_multiplier = 1
            if leave.half_day:
                leave_multiplier = 0.5
            leave_detail.append({
               'leave_type': leave.type.type,
                'from_date': leave.from_date,
                'to_date': leave.to_date,
                'days':  ((leave.to_date - leave.from_date).days + 1) * leave_multiplier,
                'id':leave.id,
                'half_day':leave.half_day,
                'leave_pending':leave.leave_pending,
                'leave_approved': leave.leave_approved
            })
        context.update({
            'full_name': lms_user.user.get_full_name(),
            'leaves': leave_detail,
            'image_url':image_url,
            'deapartment':lms_user.department.department,
            'phone':lms_user.phone_number
        })
        return JsonResponse({"status":True, "payload":context},status=200)
    except (lms_user_models.LmsUser.DoesNotExist, Exception) as e:
        print(e)
        return JsonResponse({"status":False, "message":"Error"}, status = 500)


@csrf_exempt
@api_view(["GET"])
def generate_compensationReport(request):
    if not is_leave_issuer(request.user):
        return JsonResponse({"status":False, "message":"Not authorized to view this"}, status=400)
    try:
        lms_user_id = lms_user_models.LmsUser.objects.get(user=request.user)
        compensation = leave_manager.get_user_compensationLeave_detail(lms_user_id.id,request.user)
        context = {}
        context.update({'compensation':compensation})
        return JsonResponse({"status":True, "payload":context},status=200)
    except (lms_user_models.LmsUser.DoesNotExist, Exception) as e:
        print(e)
        return JsonResponse({"status":False, "message":"Error"}, status = 500)


@csrf_exempt
@api_view(["GET"])
def compensationLeave_detail(request, id):
    user_detail = {}
    compensation_leave = {}
    try:
        leave = leave_models.CompensationLeave.objects.get(id=id)
        image_url = get_image_url_mobile(leave.user, request, 'user' ,None)
        user_detail.update({
                'full_name': leave.user.user.get_full_name(),
                'phone_number': leave.user.phone_number,
                'department':leave.user.department.department,
                'phone':leave.user.phone_number,
                'image': image_url,
                'no_of_days': leave.days,
                'reason': leave.reason,
                'leave_pending': leave.leave_pending,
                'leave_approved':leave.leave_approved
            })
        print(leave)
        context = {}
        context.update({'user_detail':user_detail})
        return JsonResponse({"status":True, "payload":context},status=200)
    except (leave_models.CompensationLeave.DoesNotExist, Exception) as e:
        print(e)
        return JsonResponse({"status":False, "message":"Error"}, status = 500)


@csrf_exempt
@api_view(["GET"])
def generate_report_byPerson(request, id):
    if not is_leave_issuer(request.user):
        return JsonResponse({"status":False, "message":"Not authorized to view this"}, status=400)
    try:
        lms_user = lms_user_models.LmsUser.objects.get(user__id=id)
        leave_list = leave_models.Leave.objects.order_by("-id").filter(from_date__month__gte = 4, user__id=lms_user.id)
        leave = []
        for leaves in leave_list:
            if leaves.from_date.month == 4:
                if (leaves.from_date.day<14 and leaves.to_date.day>=14) or leaves.from_date.day>=14:
                    leave.append(leaves)
            else:
                leave.append(leaves)
        context = {}
        detail_leave = leave_manager.get_data(leave)
        context.update({'leave_of_lmsUser':detail_leave})
        context.update({'lms_user':lms_user.user.get_full_name()})
        return JsonResponse({"status":True, "payload":context},status=200)
    except (lms_user_models.LmsUser.DoesNotExist, Exception) as e:
        print(e)
        return JsonResponse({"status":False, "message":"Error"}, status=500)


@csrf_exempt
@api_view(["POST"])
@parser_classes((MultiPartParser, FormParser,))
def add_holiday(request,format=None):    
    if not is_leave_issuer(request.user):
        return JsonResponse({"status":False, "message":"Not authorized to view this"}, status=400)
    if request.method == "POST":
        holiday = {}
        serializer = mobile_api_serializers.HolidaySerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            holiday_obj = leave_models.Holiday.objects.order_by("-id").filter(title = request.data['title'])[0]
            image_url = get_image_url_mobile(None, request, 'holiday' ,holiday_obj.id)
            holiday.update({
                "id":holiday_obj.id,
                "title":request.data["title"],
                "from_date": request.data["from_date"],
                "to_date": request.data["to_date"],
                "description": request.data["description"],
                "image": image_url
            })
            return JsonResponse({"status":True, "payload":holiday}, status=201)
        else:
            return JsonResponse({"status":False, "message":"Holiday not created"},status = 400)


@csrf_exempt
@api_view(["POST"])
@parser_classes((MultiPartParser, FormParser,))               
def update_holiday(request, id):
    try:
        if not is_leave_issuer(request.user):
            return JsonResponse({"status":False, "message":"Not authorized to view this"}, status=400)
        if request.method == "POST":
            holiday = {}
            holiday_obj = leave_models.Holiday.objects.get(id = id)
            serializer = mobile_api_serializers.HolidaySerializer(holiday_obj,data = request.data)
            if serializer.is_valid():
                serializer.save()
                image_url = get_image_url_mobile(None, request, 'holiday' ,holiday_obj.id)
                holiday.update({
                    "id":holiday_obj.id,
                    "title":request.data["title"],
                    "from_date": request.data["from_date"],
                    "to_date": request.data["to_date"],
                    "description": request.data["description"],
                    "image": image_url
                })
                return JsonResponse({"status":True, "payload":holiday}, status=200)
            else:
                return JsonResponse({"status":False, "message":"Invalid Data"},status = 400)
    except (leave_models.Holiday.DoesNotExist, Exception ) as e:
        print(e)
        return JsonResponse({"status":False, "message":"Holiday not updated"},status = 500)

@csrf_exempt
@api_view(["POST"])              
def delete_holiday(request, id):
    try:
        if not is_leave_issuer(request.user):
            return JsonResponse({"status":False, "message":"Not authorized to view this"}, status=400)
        holiday = leave_models.Holiday.objects.get(id = id)
        holiday.delete()
        return JsonResponse({"status":True, "payload":"Holiday deleted sucessfully"}, status=200)
    except (leave_models.Holiday.DoesNotExist, Exception ) as e:
        print(e)
        return JsonResponse({"status":False, "message":"Holiday not deleted"},status = 400)


@csrf_exempt
@api_view(["POST"])
@parser_classes((MultiPartParser, FormParser,))  
def change_user_photo(request,id):
    try:
        if request.method == "POST":
            image = {}
            user = lms_user_models.LmsUser.objects.get(id = id)
            serializer = mobile_api_serializers.ChangeUserPhotoSerailizer(user, data = request.data)
            if serializer.is_valid():
                serializer.save()
                image_url = get_image_url_mobile(user, request, 'user' ,None)
                image.update({
                    'image':image_url
                })
                return JsonResponse({"status":True,"payload":image},status = 200)
    except (lms_user_models.LmsUser.DoesNotExist, Exception) as e:
        print(e)
        return JsonResponse({},status = 500)


@csrf_exempt
@api_view(["POST"])
def change_user_phone_number(request,id):
    try:
        if request.method == "POST":
            phone_number = {}
            user = lms_user_models.LmsUser.objects.get(id = id)
            serializer = mobile_api_serializers.ChangeUserPhoneSerailizer(user, data = request.data)
            if serializer.is_valid():
                serializer.save()
                phone_number.update({
                    'phone_number':request.data['phone_number']
                })
                return JsonResponse({"status":True,"payload":phone_number},status = 200)
    except (lms_user_models.LmsUser.DoesNotExist, Exception) as e:
        print(e)
        return JsonResponse({},status = 500)


@csrf_exempt
@api_view(["PUT"])
def change_password(request):
    user = request.user
    serializer = mobile_api_serializers.PasswordSerializer(data=request.data)
    if serializer.is_valid():
        if not request.data['old_password'] == request.data['new_password']:
            if request.data['new_password'] == request.data['confirm_password']:
                if not user.check_password(serializer.data.get('old_password')):
                    return JsonResponse({'status':False,'message': 'Wrong password.'}, status=400)
                else:
                    if send_mail.send_email(request,request.user,'Password Change'):
                        # set_password also hashes the password that the user will get
                        user.set_password(serializer.data.get('new_password'))
                        user.save()
                        return JsonResponse({'status':True,'message':'Password changed sucessfully'}, status=200)
                    else:
                        return JsonResponse({'status':False,'message': 'Email not sent'}, status=400)
            else:
                return JsonResponse({'status':False,'message': 'Passwords do not match.'}, status=400)
        else:
            return JsonResponse({'status':False,'message': 'New password should not be old password'}, status=400)
    return JsonResponse({'status':False,'error':serializer.errors}, status=400)


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def password_reset(request):
    try:
        serializer = mobile_api_serializers.PasswordResetSerializer(data =request.data)
        if serializer.is_valid():
            user = User.objects.get(email=request.data['email'])
            if user:
                if send_mail.send_email(request,user,'Password Reset Mobile'):
                    return JsonResponse({'status':True,'message':'Email has been sent for password reset'}, status=200)
                else:
                    return JsonResponse({'status':False,'message':'Email not sent'}, status=400)
            else:
                return JsonResponse({'status':False,'message':'Email not sent'}, status =400)
        return JsonResponse({'status':False,'error':serializer.errors}, status=400)
    except (lms_user_models.User.DoesNotExist, Exception) as e:
        print(e)
        return JsonResponse({'status':False,'error':''}, status=500)



@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def token_verify(request,token):
    try:
        decoded = jwt.decode(token, credentials['secret'], algorithms='HS256',options={'verify_exp': False})
        user =User.objects.get(email=decoded['email'])
        exp = decoded['expires']
        if exp > str(datetime.now()):
            user_id = {'id':user.pk} 
            return JsonResponse({"status":True,"data":user_id})
        else:
            return JsonResponse({"status":False, "message":"Invalid Token"})
    except (User.DoesNotExist, Exception) as e:
        print(e)
        return JsonResponse({"status":False, "message":"Invalid Token"})


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def password_reset_done(request, pk):
    try:
        user = User.objects.get(pk =pk)
    except (User.DoesNotExist, Exception):
        user = None
    if user:
        validlink = True
        serializer = mobile_api_serializers.PasswordResetDoneSerializer(data =request.data)
        if serializer.is_valid() and send_mail.send_email(request,user,'Password Change') and validlink:
            user.set_password(serializer.data.get('new_password'))
            user.save()
            return JsonResponse({'status':True,'message':'Password reset successful'}, status=200)
        else:
            return JsonResponse({'status':False,'message':serializer.errors}, status=400)
    else:
        return JsonResponse({'status':False,'message':'Token not valid'}, status=400)
    

def doc(request):
    return render(request,'mobile_api/doc.html')
