import json
from lms_api.models import APIToken
from django.http import JsonResponse
from leave_rhymes.models import Rhyme, RhymeType
from django.views.decorators.csrf import csrf_exempt
from leave_manager.common.users import get_birthday_today
from leave_manager.common.leave_manager import get_leave_today, get_user_leave_detail_monthly
from leave_manager.models import Holiday
import datetime
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.contrib.auth.models import User
# Create your views here.
@csrf_exempt
def index_view(request):
    try:
        api_key = json.loads(request.body.decode('utf-8'))['api_key']
        if APIToken.objects.get(api_key=api_key):
            return JsonResponse({
                'data': 'Token Works',
            }, status=200)
        else:
            return JsonResponse({
                'api_key': request.POST['api_key'],
                'data': 'Token False'
            }, status=401)
    except Exception as e:
        print('Bad Key', e)
        return JsonResponse({
            'data': 'Some Thing went wrong'
        }, status=500)


@csrf_exempt
def birthday_view(request):
    try:
        api_key = json.loads(request.body.decode('utf-8'))['api_key']
        if APIToken.objects.get(api_key=api_key):
            birthdays = get_birthday_today()
            return JsonResponse({
                'data': birthdays
            }, status=200)
        else:
            return JsonResponse({
                'message': 'Token False',
                'api_key': request.POST['api_key']
            }, status=401)
    except Exception as e:
        print('Bad Key', e)
        return JsonResponse({
            'data': 'Something Went Wrong'
        }, status=500)


@csrf_exempt
def leave_view(request):
    try:
        api_key = json.loads(request.body.decode('utf-8'))['api_key']
        if APIToken.objects.get(api_key=api_key):
            leaves = get_leave_today()
            return JsonResponse({
                'data': leaves
            }, status=200)
        else:
            return JsonResponse({
                'data': 'Token False',
                'api_key': request.POST['api_key']
            }, status=401)
    except Exception as e:
        print('Bad Key', e)
        return JsonResponse({
            'data': 'Something Went Wrong'
        }, status=500)


@csrf_exempt
def monthly_detail_view(request):
    try:
        api_key = json.loads(request.body.decode('utf-8'))['api_key']
        lms_user_id = int(json.loads(request.body.decode('utf-8'))['user'])
        month = int(json.loads(request.body.decode('utf-8'))['month'])
        if APIToken.objects.get(api_key=api_key):
            return JsonResponse({
                'data': get_user_leave_detail_monthly(lms_user_id, month)
            }, status=200)
    except Exception as e:
        print('Bad Key', e)
        return JsonResponse({
            'data': 'Something Went Wrong'
        }, status=500)


@csrf_exempt
def no_leave_rhyme_view(request):
    try:
        api_key = json.loads(request.body.decode('utf-8'))['api_key']
        if APIToken.objects.get(api_key=api_key):
            return JsonResponse({
                'data': Rhyme.objects.filter(type=RhymeType.objects.get(type='No Leave Rhyme')).order_by(
                    '?').first().rhyme
            }, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({}, status=500)


@csrf_exempt
def all_hands_rhyme_view(request):
    try:
        api_key = json.loads(request.body.decode('utf-8'))['api_key']
        if APIToken.objects.get(api_key=api_key):
            return JsonResponse({
                'data': Rhyme.objects.filter(type=RhymeType.objects.get(type='All Hands Rhyme')).order_by(
                    '?').first().rhyme
            }, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({}, status=500)


@csrf_exempt
def company_holidays(request):
    try:
        api_key = json.loads(request.body.decode('utf-8'))['api_key']
        if APIToken.objects.get(api_key=api_key):
            tomorrow_holiday = is_holiday()
            return JsonResponse({
                'data': tomorrow_holiday
            }, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({}, status=500)


def is_holiday():
    today = datetime.datetime.today()
    tomorrow = today+datetime.timedelta(1)  
    try:
        holidays = Holiday.objects.filter(from_date=tomorrow)
        for holiday in holidays:
            d2 = datetime.datetime.strptime(str(holiday.to_date), "%Y-%m-%d")
            d1 = datetime.datetime.strptime(str(holiday.from_date), "%Y-%m-%d")
            days = abs(d2-d1).days+1
            
            msg = f"Holiday Update.\n We have holidays for: {holiday.title}\nFrom Date: {holiday.from_date}\nTo Date: {holiday.to_date}\nTotal Days:{days} days\n Have a great time."
            if days == 1:
                msg = f"Holiday Update.\n We have holiday for: {holiday.title}\nOn:{holiday.from_date}\nTotal Day:{days} day\n Have a great time."
        return msg
    except Holiday.DoesNotExist:
        return msg

        