import datetime
from lms_user.models import LmsUser
from leave_manager.common import users
from leave_manager.common import leave_manager
from leave_manager.models import LeaveType, Holiday, CompensationLeave
from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect, Http404
from django.http import HttpResponse
from django.contrib import messages
from leave_manager.common import leave_manager
from leave_manager.common.my_info import get_lms_user
from leave_manager.common.my_info import get_user_photo_for_edit
from leave_manager.common.check_leave_admin import is_leave_issuer
from leave_manager.common.routes import get_formatted_routes, get_routes
from leave_manager.models import Leave
from django.shortcuts import get_object_or_404
import calendar
from django.contrib.auth.models import User
import pusher
from pusher import Pusher
from django.views.decorators.csrf import csrf_exempt
import base64
from django.core.files.base import ContentFile
from leave_rhymes.models import Rhyme,RhymeType
from leave_manager.common import check_leave_admin
from leave_manager.forms import HolidayForm
import yaml


credentials = yaml.load(open('credentials.yaml'))
pusher_client = pusher.Pusher(
  app_id=credentials['pusher_app_id'],
  key=credentials['pusher_key'],
  secret=credentials['pusher_secret'],
  cluster=credentials['pusher_cluster'],
  ssl=credentials['pusher_ssl']
)

def get_dashboard(request):
    # context = {}
    # if not request.user.is_authenticated:
    #     return HttpResponseRedirect(reverse('user-login'))
    # else:
    #     routes = get_formatted_routes(get_routes(request.user), active_page='dashboard')
    #     context.update({'routes': routes})
    #     return render(request, 'leave_manager/dashboard.html', context=context)
    return HttpResponseRedirect(reverse('leave_manager_my_profile'))


def get_my_profile(request):
    context = {}
    leaves = leave_manager.get_all_leaves_unseen()
    context.update({'leave_notify':leaves})
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))
    else:
        lms_user = get_lms_user(request.user)
        context.update({'user_detail': lms_user})
        routes = get_formatted_routes(get_routes(request.user), active_page='my profile')
        context.update({'routes': routes})
        return render(request, 'leave_manager/profile.html', context=context)


def get_notifications(request):
    context = {}
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))
    else:
        routes = get_formatted_routes(get_routes(request.user), active_page='notifications')
        context.update({'routes': routes})
        return render(request, 'leave_manager/notifications.html', context=context)


def get_leave_today(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))

    context = {}
    leaves = leave_manager.get_all_leaves_unseen()
    context.update({'leave_notify':leaves})
    
    leaves_today = leave_manager.get_leave_today()
    routes = get_formatted_routes(get_routes(request.user), active_page='leave today')
    context.update({
        'routes': routes,
        'leaves_today': leaves_today
    })
    return render(request, 'leave_manager/leave_today.html', context=context)


def get_users(request):
    context = {}
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))
    else:
        generate_report_access = False
        if check_leave_admin.is_leave_issuer(request.user):
            generate_report_access = True
        lms_users = users.get_lms_users()
        context.update({'lms_users': lms_users})
        context.update({'generate_report_access': generate_report_access})
        routes = get_formatted_routes(get_routes(request.user), active_page='users')
        context.update({'routes': routes})
        return render(request, 'leave_manager/users.html', context=context)


def apply_leave(request):

    leave_types = LeaveType.objects.all()
    routes = get_formatted_routes(get_routes(request.user), active_page='apply leave')
    context = {'leave_types': leave_types}
    context.update({'routes': routes})
    leaves = leave_manager.get_all_leaves_unseen()
    leaves += 1
    context.update({'leave_notify':leaves})
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))
    if request.method == 'POST':
        leave_details = {
            'user': LmsUser.objects.get(user=request.user),
            'from_date': datetime.datetime.strptime(request.POST['from_date'], '%Y-%m-%d'),
            'to_date': datetime.datetime.strptime(request.POST['to_date'], '%Y-%m-%d'),
            'leave_type': LeaveType.objects.get(id=request.POST['leave_type']),
            'leave_reason': request.POST['leave_reason'],
            'issuer': LmsUser.objects.get(user=request.user).leave_issuer,
            'half_day': False,
            'leave_multiplier': 1
        }
        if leave_manager.half_leave_applied(request=request):
            leave_details.update({
                'half_day': True,
                'leave_multiplier': 0.5
            })
       
       
        if leave_manager.apply_leave(request=request, leave_details=leave_details):
            pusher_client.trigger('my-channel', 'my-event', leaves)
            return HttpResponseRedirect(reverse('leave_manager_dashboard'))
        else:              
            pusher_client.trigger('my-channel', 'my-event', leaves)
            context.update({'message': 'Could Not Apply Leave. Please Contact Admin'})
            return render(request, 'leave_manager/apply_leave.html', context=context)

    else:
        return render(request, 'leave_manager/apply_leave.html', context=context)

def get_leave_requests(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))

    context = {}
    leaves = leave_manager.get_all_leaves_unseen()
    context.update({'leave_notify':leaves})
    routes = get_formatted_routes(get_routes(request.user), active_page='leave requests')
    context.update({'routes': routes})
    context.update({'leave_requests': leave_manager.get_leave_requests(request.user)})
    context.update({'compensationLeave_requests': leave_manager.get_compensationLeave_requests(request.user)})
    return render(request, 'leave_manager/leave_requests.html', context=context)


def get_leave_requests_by_id(request, id):
    context = {}
    leaves = leave_manager.get_all_leaves_unseen()
    context.update({'leave_notify':leaves})
    routes = get_formatted_routes(get_routes(request.user), active_page='leave requests')
    context.update({'routes': routes})
    context.update({'leave_requests': leave_manager.get_leave_requests(request.user)})

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))
    if not is_leave_issuer(request.user):
        return HttpResponseRedirect(reverse('leave_manager_dashboard'))

    leave = Leave.objects.get(id=id)
    leave.notification = False
    leave.save()

    if request.method == 'POST':
        if request.POST['leave_response'] == '2':
            if leave_manager.reject_leave_request(request=request, leave_id=int(request.POST['leave_id'])):
                context.update({'leave_requests': leave_manager.get_leave_requests(request.user)})
                context.update({
                    'leave_response_success': True,
                    'message': 'Reject Success'
                })
                pusher_client.trigger('my-leave-notify', 'my-event2', "Leave rejected ")
                return render(request, 'leave_manager/leave_requests.html', context=context)
            else:
                context.update({'leave_requests': leave_manager.get_leave_requests(request.user)})
                context.update({
                    'leave_response_success': False,
                    'message': 'Reject Failed'
                })
                pusher_client.trigger('my-leave-notify', 'my-event2', "Leave rejeted failed")
                return render(request, 'leave_manager/leave_requests.html', context=context)

        elif request.POST['leave_response'] == '1':
            if leave_manager.approve_leave_request(request=request, leave_id=int(request.POST['leave_id'])):
                context.update({'leave_requests': leave_manager.get_leave_requests(request.user)})
                context.update({
                    'leave_response_success': True,
                    'message': 'Approve Success'
                })
                pusher_client.trigger('my-leave-notify', 'my-event2', "Leave approved")
                return render(request, 'leave_manager/leave_requests.html', context=context)
            else:
                context.update({'leave_requests': leave_manager.get_leave_requests(request.user)})
                context.update({
                    'leave_response_success': False,
                    'message': 'Approve Failed'
                })
                pusher_client.trigger('my-leave-notify', 'my-event2', "Leave approved reject")
                return render(request, 'leave_manager/leave_requests.html', context=context)
    else:
        context.update({'leave_requests': leave_manager.get_leave_requests_by_id(request.user, id)})
        return render(request, 'leave_manager/leave_requests_details.html', context=context)


def get_birthday_today(request):
    context = {}
    leaves = leave_manager.get_all_leaves_unseen()
    context.update({'leave_notify':leaves})
    routes = get_formatted_routes(get_routes(request.user), active_page='birthdays')
    context.update({'routes': routes})
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))
    else:
        birthday_today = users.get_birthday_today()['users']
        context.update({'birthdays': birthday_today})
        upcoming_bday = users.get_birthday_today()['upcoming']

        upcoming_bday_visible = False
        if is_leave_issuer(request.user):
            upcoming_bday_visible = True
            context.update({'upcoming_bday': upcoming_bday})
            context.update({'upcoming_bday_visible': upcoming_bday_visible})
        return render(request, 'leave_manager/birthdays.html', context=context)


def generate_report(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))
    if not is_leave_issuer(request.user):
        return HttpResponseRedirect(reverse('leave_manager_dashboard'))
        
    context = {}
    routes = get_formatted_routes(get_routes(request.user), active_page='leave report')
    context.update({'routes': routes})
    if request.method == "POST":
        from_date = datetime.datetime.strptime(request.POST['from_date'], '%Y-%m-%d').date()
        to_date = datetime.datetime.strptime(request.POST['to_date'], '%Y-%m-%d').date()
        leave_list = leave_manager.get_users_leaveDetailFor_searchEngine(request.user,from_date,to_date)
        # name_list = leave_manager.get_users_leaveDetailFor_searchEngine(request.user,from_date,to_date)
        if leave_list == {}:
            context.update({'reports':" "})            
        else:
            context.update({'reports':sorted(leave_list.items())})
        context.update({'from_date':from_date})
        context.update({'to_date':to_date})
        return render(request, "leave_manager/leaveReportGenerator.html", context = context)

    else:
        return render(request, "leave_manager/leaveReportGenerator.html", context = context)


def leave_detail(request, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))
        
    leave = get_object_or_404(Leave, id=id)
    context = {}
    leaves = leave_manager.get_all_leaves_unseen()
    context.update({'leave_notify':leaves})
    routes = get_formatted_routes(get_routes(request.user), active_page='leave report')
    context.update({'routes': routes})
    context.update({'leave':leave})
    return render(request, "leave_manager/leave-detail.html", context=context)


def compensationLeave_detail(request, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))

    user_detail = {}
    leave = get_object_or_404(CompensationLeave, id=id)
    try:
        image_url = leave.user.image.url.split('/static/')[1]
    except Exception as e:
        print(e)
        image_url = 'lms_user/images/photograph.png'

    user_detail.update({
            'full_name': leave.user.user.get_full_name(),
            'phone_number': leave.user.phone_number,
            'department':leave.user.department,
            'phone':leave.user.phone_number,
            'image': image_url,
        })

    context = {}
    routes = get_formatted_routes(get_routes(request.user), active_page='leave report')
    context.update({'routes': routes})
    context.update({'leave':leave})
    context.update({'user_detail':user_detail})
    return render(request, "leave_manager/compensationLeave-detail.html", context=context)


def change_user_number(request, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))

    user = LmsUser.objects.get(id=id)
    if request.method == "POST":
        new_number = request.POST['new-number']
        if new_number:
            if user:
                user.phone_number = new_number
                user.save()
        return HttpResponseRedirect(reverse('leave_manager_my_profile'))
    else:
        context = {}
        leaves = leave_manager.get_all_leaves_unseen()
        context.update({'leave_notify':leaves})
        routes = get_formatted_routes(get_routes(request.user), active_page='my profile')
        context.update({'routes': routes})
        context.update({'user':user})
        return render(request,"leave_manager/edit-phone.html",context=context)


def crop_user_photo(request, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))

    context = {}
    leaves = leave_manager.get_all_leaves_unseen()
    context.update({'leave_notify':leaves})
    routes = get_formatted_routes(get_routes(request.user), active_page = "my profile")
    context.update({'routes':routes})
    user = get_user_photo_for_edit(id)
    context.update({'users':user})
    return render(request, "leave_manager/crop-photo.html", context=context)

def edit_user_photo(request, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))

    lms_user = LmsUser.objects.get(user__id=id)
    if request.method == "POST":
        new_image = request.POST.get('link-taker')
        format = new_image.split(';base64,')[1]
        # ext = format.split('/')[1] 
        date = datetime.date.today()
        data = ContentFile(base64.b64decode(format), name=str(date) + request.user.first_name) # You can save this as file instance.
        if new_image:
            lms_user.image = data
            lms_user.save()
        return HttpResponseRedirect(reverse('leave_manager_my_profile'))      


def generate_holidays(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))

    context = {}
    routes = get_formatted_routes(get_routes(request.user), active_page = "company holidays")
    context.update({'routes':routes})
    holidays = leave_manager.get_holidays(request)
    context.update({'holidays':holidays})
    if check_leave_admin.is_leave_issuer(request.user):
        context.update({'leave_issuer':1})
    return render(request, "leave_manager/holidays/index.html", context=context)
    

def add_new_holidays(request):
    if not request.user.is_authenticated:
        url = reverse('user-login')
        return HttpResponseRedirect(url)

    context = {}
    routes = get_formatted_routes(get_routes(request.user), active_page = "company holidays")
    context.update({'routes':routes})
    
    # if request.method == "POST":
    #     title = request.POST['title']
    #     from_date = datetime.datetime.strptime(request.POST['from_date'], '%Y-%m-%d')
    #     to_date = datetime.datetime.strptime(request.POST['to_date'], '%Y-%m-%d')
    #     description = request.POST['description']
    #     Holiday.objects.create(title=title, from_date=from_date,to_date=to_date,description=description)
    #     return HttpResponseRedirect(reverse('company-holiday'))
    # else:   
    #     return render(request, 'leave_manager/holidays/create.html', context=context)
    form = HolidayForm(request.POST, request.FILES)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('company-holiday'))
        else:
            form = HolidayForm()
            context.update({'form':form})
        return render(request, 'leave_manager/holidays/create.html', context=context)
    else:
        form = HolidayForm()
        context.update({'form':form})

    return render(request, 'leave_manager/holidays/create.html', context=context)


def update_company_holidays_by_id(request,id):
    if not request.user.is_authenticated:
        url = reverse('user-login')
        return HttpResponseRedirect(url)
        

    if request.method == "POST":
        instance = get_object_or_404(Holiday, id=id)
        form = HolidayForm(request.POST or None, instance=instance)
        if form.is_valid():
            form.save(commit=False)
            try:
                image = request.FILES['image']
                instance.image = image
            except Exception as e:
                print(e)
            instance.save()
            messages.success(request, "Holiday has been successfully updated.", extra_tags="1")
        else:
            messages.success(request, "Holiday was unable to update. Please try again.", extra_tags="0")
        return HttpResponseRedirect(reverse('company-holiday'))
        # if Holiday.objects.filter(id=id).update(title=request.POST['title'],from_date=request.POST['from_date'],to_date=request.POST['to_date'],description=request.POST['description']):
        #     messages.success(request, "Holiday has been successfully updated.", extra_tags="1")
        # else:
        #     messages.success(request, "Holiday eas unable to update. Please try again.", extra_tags="0")
        # return HttpResponseRedirect(reverse('company-holiday'))
    else:
        try:
            holiday = Holiday.objects.get(id=id)
            context = {}
            leaves = leave_manager.get_all_leaves_unseen()
            context.update({'leave_notify':leaves})
            routes = get_formatted_routes(get_routes(request.user), active_page = "company holidays")
            context.update({'routes':routes})
            context.update({'holiday':holiday})
            from_date_month = holiday.from_date.month
            from_date_day = holiday.from_date.day

            if from_date_month<10:
                from_date_month = "0"+str(holiday.from_date.month)
            if from_date_day<10:
                from_date_day = "0"+str(holiday.from_date.day)

            from_date = str(holiday.from_date.year)+'-'+str(from_date_month)+'-'+str(from_date_day)

            to_date_month = holiday.to_date.month
            to_date_day = holiday.to_date.day

            if to_date_month<10:
                to_date_month = "0"+str(holiday.to_date.month)
            if to_date_day<10:
                to_date_day = "0"+str(holiday.to_date.day)

            to_date = str(holiday.to_date.year)+'-'+str(to_date_month)+'-'+str(to_date_day)
            context.update({'from_date':from_date})
            context.update({'to_date':to_date})
            total_days_of_holiday = leave_manager.get_totalDays_ofEach_holidays(holiday.from_date,holiday.to_date)
            context.update({'total_days':total_days_of_holiday})
            return render(request, "leave_manager/holidays/update.html", context=context)
        except Exception as e:
            raise Http404


def delete_company_holidays_by_id(request, id):
    try:
        if not request.user.is_authenticated:
            url = reverse('user-login')
            return HttpResponseRedirect(url)
        else:
            holiday = Holiday.objects.filter(id=id)
            holiday.delete()
            return HttpResponseRedirect(reverse('company-holiday'))
    except Exception as e:
        print(e)
        return e


@csrf_exempt
def notify():
    leaves = Leave.objects.get(notification = True)
    return HttpResponse("done")


def generate_rhymes(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))

    rhymes = Rhyme.objects.order_by("-id").all()
    context = {}
    routes = get_formatted_routes(get_routes(request.user), active_page = "rhymes")
    context.update({'routes':routes})
    context.update({'rhymes':rhymes})
    return render(request, "leave_manager/rhymes/index.html",context = context)


def update_rhyme_by_id(request, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))

    rhymes = get_object_or_404(Rhyme, id=id)
    rhyme_type = RhymeType.objects.all()

    if request.method == "POST":
        rhymes.title = request.POST['title']
        rhymes.rhyme = request.POST['rhyme']
        type = RhymeType.objects.get(id=request.POST['type'])
        rhymes.type = type
        rhymes.save()
        return HttpResponseRedirect(reverse('rhymes'))
    else:
        try:
            context = {}
            routes = get_formatted_routes(get_routes(request.user), active_page = "rhymes")
            context.update({'routes':routes})
            context.update({'rhymes':rhymes})
            context.update({'rhyme_type':rhyme_type})
            return render(request, "leave_manager/rhymes/update.html", context=context)
        except Exception as e:
            print("Error:"+e)
            return e


def delete_rhyme_by_id(request, id):
    try:
        if not request.user.is_authenticated:
            url = reverse('user-login')
            return HttpResponseRedirect(url)
        else:
            rhyme = Rhyme.objects.filter(id=id).delete()
            return HttpResponseRedirect(reverse('rhymes'))
    except Exception as e:
        print(e)
        return e


def add_new_rhymes(request):
    if not request.user.is_authenticated:
        url = reverse('user-login')
        return HttpResponseRedirect(url)
    context = {}
    rhyme_type = RhymeType.objects.all()
    routes = get_formatted_routes(get_routes(request.user), active_page = "rhymes")
    context.update({'routes':routes})
    context.update({'rhyme_type':rhyme_type})
    if request.method == "POST":
        title = request.POST['title']
        rhyme = request.POST['rhyme']
        type = RhymeType.objects.get(id=request.POST['type'])
        Rhyme.objects.create(title=title, rhyme=rhyme,type=type)
        return HttpResponseRedirect(reverse('rhymes'))
    else:   
        return render(request, 'leave_manager/rhymes/create.html', context=context)



def generate_rhymeTypes(request):
    if not request.user.is_authenticated:
        url = reverse('user-login')
        return HttpResponseRedirect(url)
    rhymeTypes = RhymeType.objects.order_by("-id").all()
    context = {}
    routes = get_formatted_routes(get_routes(request.user), active_page = "rhymes")
    context.update({'routes':routes})
    context.update({'rhymeTypes':rhymeTypes})
    return render(request, "leave_manager/rhymes/rhyme_type/index.html",context = context)


def update_rhymeTypes_by_id(request, id):
    if not request.user.is_authenticated:
        url = reverse('user-login')
        return HttpResponseRedirect(url)
    rhyme_type = RhymeType.objects.get(id=id)

    if request.method == "POST":
        rhyme_type.type = request.POST['type']
        rhyme_type.save()
        return HttpResponseRedirect(reverse('rhymeTypes'))
    else:
        try:
            context = {}
            routes = get_formatted_routes(get_routes(request.user), active_page = "rhymes")
            context.update({'routes':routes})
            context.update({'rhyme_type':rhyme_type})
            return render(request, "leave_manager/rhymes/rhyme_type/update.html", context=context)
        except Exception as e:
            print(e)
            return e


def delete_rhymeTypes_by_id(request, id):
    try:
        if not request.user.is_authenticated:
            url = reverse('user-login')
            return HttpResponseRedirect(url)
        else:
            rhymType_rhyme = Rhyme.objects.filter(type__id=id)
            if rhymType_rhyme:
                messages.success(request, 'Cannot Delete Rhyme Type. This rhyme type may contains some rhymes.')
            else:
                RhymeType.objects.filter(id=id).delete()
        return HttpResponseRedirect(reverse('rhymeTypes'))
    except Exception as e:
        print(e)
        return e


def  add_new_rhymeType(request):
    if not request.user.is_authenticated:
        url = reverse('user-login')
        return HttpResponseRedirect(url)
    context = {}
    routes = get_formatted_routes(get_routes(request.user), active_page = "rhymes")
    context.update({'routes':routes})
    if request.method == "POST":
        RhymeType.objects.create(type=request.POST['type'])
        return HttpResponseRedirect(reverse('rhymeTypes'))
    else:   
        return render(request, 'leave_manager/rhymes/rhyme_type/create.html', context=context)


def leaveHistory(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))

    context = {}
    routes = get_formatted_routes(get_routes(request.user), active_page='my leave history')
    context.update({'routes': routes})
    date = datetime.date.today()
    lms_user = LmsUser.objects.filter(user__id=request.user.id)[0]
    data = leave_manager.get_own_leave_detail_monthly(lms_user.id, date.month)
    compensation_data = leave_manager.get_own_compensationLeave_detail_monthly(lms_user.id)
    context.update({"date":date})
    context.update({"leave":data})
    context.update({"compensation_leave":compensation_data})
    return render(request, "leave_manager/my_leave_data.html", context = context)


def apply_compensationLeave(request):

    context = {}
    routes = get_formatted_routes(get_routes(request.user), active_page='apply compensation')
    context.update({'routes': routes})
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))
    if request.method == 'POST':
        leave_details = {
            'user': LmsUser.objects.get(user=request.user),
            'leave_reason': request.POST['leave_reason'],
            'issuer': LmsUser.objects.get(user=request.user).leave_issuer,
            'days':request.POST['days']
        }
       
        if leave_manager.apply_CompensationLeave(request=request, leave_details=leave_details):
            pusher_client.trigger('my-channel', 'my-event', {})
            return HttpResponseRedirect(reverse('leave_manager_dashboard'))
        else:              
            pusher_client.trigger('my-channel', 'my-event', {})
            context.update({'message': 'Could Not Apply Leave. Please Contact Admin'})
            return render(request, 'leave_manager/apply_compensationLeave.html', context=context)

    else:
        return render(request, 'leave_manager/apply_compensationLeave.html', context=context)


def leave_manager_compensationLeave_requests_by_id(request, id):
    context = {}
    routes = get_formatted_routes(get_routes(request.user), active_page='leave requests')
    context.update({'routes': routes})
    context.update({'leave_requests': leave_manager.get_leave_requests(request.user)})

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))
    if not is_leave_issuer(request.user):
        return HttpResponseRedirect(reverse('leave_manager_dashboard'))

    leave = CompensationLeave.objects.get(id=id)
    leave.notification = False
    leave.save()

    if request.method == 'POST':
        if request.POST['leave_response'] == '2':
            if leave_manager.reject_compensationLeave_request(request=request, leave_id=int(request.POST['leave_id'])):
                context.update({'leave_requests': leave_manager.get_compensationLeave_requests(request.user)})
                context.update({
                    'leave_response_success': True,
                    'message': 'Reject Success'
                })
                pusher_client.trigger('my-leave-notify', 'my-event2', "Leave rejected ")
                return render(request, 'leave_manager/leave_requests.html', context=context)
            else:
                context.update({'leave_requests': leave_manager.get_compensationLeave_requests(request.user)})
                context.update({
                    'leave_response_success': False,
                    'message': 'Reject Failed'
                })
                pusher_client.trigger('my-leave-notify', 'my-event2', "Leave rejeted failed")
                return render(request, 'leave_manager/leave_requests.html', context=context)

        elif request.POST['leave_response'] == '1':
            if leave_manager.approve_compensationLeave_request(request=request, leave_id=int(request.POST['leave_id'])):
                context.update({'leave_requests': leave_manager.get_compensationLeave_requests(request.user)})
                context.update({
                    'leave_response_success': True,
                    'message': 'Approve Success'
                })
                pusher_client.trigger('my-leave-notify', 'my-event2', "Leave approved")
                return render(request, 'leave_manager/leave_requests.html', context=context)
            else:
                context.update({'leave_requests': leave_manager.get_compensationLeave_requests(request.user)})
                context.update({
                    'leave_response_success': False,
                    'message': 'Approve Failed'
                })
                pusher_client.trigger('my-leave-notify', 'my-event2', "Leave approved reject")
                return render(request, 'leave_manager/leave_requests.html', context=context)
    else:
        context.update({'compensationLeave_requests': leave_manager.get_compensationLeave_requests_by_id(request.user, id)})
        return render(request, 'leave_manager/compensationLeave_requests_details.html', context=context)


def report_details(request, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))
    if not is_leave_issuer(request.user):
        return HttpResponseRedirect(reverse('leave_manager_dashboard'))
    try:
        context = {}
        routes = get_formatted_routes(get_routes(request.user), active_page='leave report')
        context.update({'routes': routes})
        leaves = Leave.objects.filter(user__user__id=id)
        lms_user = LmsUser.objects.filter(user__pk=id)
        context.update({'leaves': leaves})
        context.update({'user_detail':lms_user})
        return render(request, "leave_manager/leaveReportDetail.html",context=context)            
    except Exception as e:
        print(e)
        return e


def generate_compensationReport(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))
    if not is_leave_issuer(request.user):
        return HttpResponseRedirect(reverse('leave_manager_dashboard'))
    try:
        lms_user_id = LmsUser.objects.filter(user=request.user)[0]
        compensation = leave_manager.get_user_compensationLeave_detail(lms_user_id.id,request.user)
        print(compensation)
        context = {}
        routes = get_formatted_routes(get_routes(request.user), active_page='leave report')
        context.update({'routes': routes})
        context.update({'compensation':compensation})
        return render(request, "leave_manager/compensation.html",context=context)
    except Exception as e:
        print(e)
        return e


def generate_report_byPerson(request, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))
    if not is_leave_issuer(request.user):
        return HttpResponseRedirect(reverse('leave_manager_dashboard'))
    
    lms_user = LmsUser.objects.get(user__id=id)
    leave_list = Leave.objects.order_by("-id").filter(from_date__month__gte = 4, user__id=lms_user.id)
    leave = []
    for leaves in leave_list:
        if leaves.from_date.month == 4:
            if (leaves.from_date.day<14 and leaves.to_date.day>=14) or leaves.from_date.day>=14:
                leave.append(leaves)
        else:
            leave.append(leaves)
            
    context = {}
    routes = get_formatted_routes(get_routes(request.user), active_page='users')
    context.update({'routes': routes})
    detail_leave = leave_manager.get_data(leave)
    context.update({'leave_of_lmsUser':detail_leave})
    context.update({'lms_user':lms_user})
    return render(request, "leave_manager/report-by-name.html", context=context)
