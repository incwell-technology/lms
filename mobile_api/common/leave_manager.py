from datetime import datetime
from leave_manager.models import Leave, CompensationLeave
from lms_user.models import LmsUser
from mobile_api.common.user_image import get_image_url_mobile
from mobile_api.common.fcm import fcm
from leave_manager.common.leave_manager import get_compensationLeave_detail

def get_leave_today_mobile(request):
    leaves_today = []
    print(datetime.today())
    for leave_request in Leave.objects.filter(from_date__lte=datetime.today(), to_date__gte=datetime.today(),
                                              leave_pending=False, leave_approved=True):
        image_url = get_image_url_mobile(leave_request.user.user,request,'user',None)
        leaves_today.append({
            'name': leave_request.user.user.get_full_name(),
            'department': leave_request.user.department.department,
            'leave_type': leave_request.type.type,
            'half_day': leave_request.half_day,
            'image': image_url
        })
    return leaves_today


def get_leave_detail(leave):
    try:
        leave_multiplier = 1
        if leave.half_day:
            leave_multiplier = 0.5
        leave_detail = {
            'id': leave.id,
            'lms_user': leave.user,
            'department': leave.user.department.department,
            'total_days': ((leave.to_date - leave.from_date).days + 1) * leave_multiplier,
            'leave_type': leave.type.type,
            'leave_reason': leave.reason,
            'half_day': leave.half_day,
        }
        return leave_detail
    except Exception as e:
        print('Could not Get Leave Detail', e)
        return {}


def check_leave_applicability(user, leave_type):
    lms_user = LmsUser.objects.get(user=user)
    if leave_type == "Annual Leave":
        if lms_user.annual_leave > 0:
            return True
    elif leave_type == "Sick Leave":
        if lms_user.sick_leave> 0:
            return True
    elif leave_type == "Compensation Leave":
        if lms_user.compensation_leave > 0:
            return True
    return False

def get_leave_requests_mobile(user):
    pending_leave_requests = []
    my_leave_approvees = LmsUser.objects.filter(leave_issuer=user)
    for leave_request in Leave.objects.order_by("-id").filter(user__in=my_leave_approvees, leave_pending=True):
        leave_multiplier = 1
        if leave_request.half_day:
            leave_multiplier = 0.5
        pending_leave_requests.append(
            {
                'id': leave_request.id,
                'full_name': leave_request.user.user.get_full_name(),
                'department': leave_request.user.department.department,
                'from_date': str(leave_request.from_date),
                'to_date': str(leave_request.to_date),
                'total_days': ((leave_request.to_date - leave_request.from_date).days + 1) * leave_multiplier,
                'leave_type': leave_request.type.type,
                'leave_reason': leave_request.reason,
                'half_day': leave_request.half_day,
                'notification':leave_request.notification
            }
        )
    return pending_leave_requests


def approve_leave_request(request, leave_id):
    try:
        leave = Leave.objects.get(id=leave_id)
        leave.leave_pending = False
        leave.leave_approved = True
        leave.save()
        leave_detail = get_leave_detail(leave)
        user = leave_detail['lms_user']
        leave_applicant = LmsUser.objects.get(user = user.user)
        leave_issuer = LmsUser.objects.get(user = leave_applicant.leave_issuer)
        fcm_token = leave_applicant.fcm_token
        if leave_detail['leave_type'] == 'Compensation Leave':
            user.compensation_leave -= leave_detail['total_days']
            if user.compensation_leave < 0:
                return False
        elif leave_detail['leave_type'] == 'Annual Leave':
            user.annual_leave -= leave_detail['total_days']
            if user.annual_leave < 0:
                return False
        elif leave_detail['leave_type'] == 'Sick Leave':
            user.sick_leave -= leave_detail['total_days']
            if user.sick_leave < 0:
                return False
        user.save()
        fcm(fcm_token, leave_issuer.user.get_full_name(), "approve_leave")
        return True
    except (Leave.DoesNotExist,LmsUser.DoesNotExist, Exception):
        return False    

def reject_leave_request(request, leave_id):
    try:
        leave = Leave.objects.get(id=leave_id)
        leave_detail = get_leave_detail(leave)
        lms_user = leave_detail['lms_user']
        leave.leave_pending = False
        leave.leave_approved = False
        leave.save()
        leave_applicant = LmsUser.objects.get(user = lms_user.user)
        leave_issuer = LmsUser.objects.get(user = leave_applicant.leave_issuer)
        fcm_token = leave_applicant.fcm_token
        fcm(fcm_token, leave_issuer.user.get_full_name(), "reject_leave")
        return True
    except (Leave.DoesNotExist,LmsUser.DoesNotExist, Exception) as e:  
        return False


def approve_compensationLeave_request(request, leave_id):
    try:
        leave = CompensationLeave.objects.get(id=leave_id)
        leave.leave_pending = False
        leave.leave_approved = True
        leave_detail = get_compensationLeave_detail(leave)
        user = leave_detail['lms_user']
        user.compensation_leave += leave_detail['days']
        user.save()
        leave.save()
        leave_issuer = LmsUser.objects.get(user = user.leave_issuer)
        fcm_token = user.fcm_token
        fcm(fcm_token, leave_issuer.user.get_full_name(), "approve_compensation")
        return True
    except (CompensationLeave.DoesNotExist, Exception) as e:
        print(e)
        return False

def reject_compensationLeave_request(request, leave_id):
    try:
        leave = CompensationLeave.objects.get(id=leave_id)
        leave_detail = get_compensationLeave_detail(leave)
        user = leave_detail['lms_user']
        leave.leave_pending = False
        leave.leave_approved = False
        leave.save()
        leave_issuer = LmsUser.objects.get(user = user.leave_issuer)
        fcm_token = user.fcm_token
        fcm(fcm_token, leave_issuer.user.get_full_name(), "reject_compensation")
        return True
    except (CompensationLeave.DoesNotExist, Exception) as e:
        print(e)
        return False


def get_compensationLeave_requests_mobile(user):
    pending_leave_requests = []
    my_leave_approvees = LmsUser.objects.filter(leave_issuer=user)
    for leave_request in CompensationLeave.objects.order_by("-id").filter(user__in=my_leave_approvees, leave_pending=True):
        pending_leave_requests.append(
            {
                'id': leave_request.id,
                'full_name': leave_request.user.user.get_full_name(),
                'department': leave_request.user.department.department,
                'leave_reason': leave_request.reason,
                'days':leave_request.days,
                'notification':leave_request.notification
            }
        )
    return pending_leave_requests

def get_own_leave_history_monthly(lms_user_id, month):
    user_detail = {}
    try:
        monthly_leave = []
        lms_user = LmsUser.objects.get(id=lms_user_id)
        user_detail.update({
            'full_name': lms_user.user.get_full_name(),
            'leaves': monthly_leave,
            })
        leaves = get_monthly_leave_detail_by_id_month(lms_user_id,month)
        for leave in leaves:
            leave_multiplier = 1
            if leave.half_day:
                leave_multiplier = 0.5
            monthly_leave.append({
                'leave_type': leave.type.type,
                'from_date': leave.from_date,
                'to_date': leave.to_date,
                'days':  ((leave.to_date - leave.from_date).days + 1) * leave_multiplier,
                'id':leave.id,
                'leave_pending':leave.leave_pending,
                'leave_approved': leave.leave_approved
            })
        user_detail.update({
            'leaves': monthly_leave
        })
        return user_detail
    except (LmsUser.DoseNotExist, Exception) as e:
        print(e)
        return user_detail

def get_own_compensationLeave_detail_monthly(lms_user_id):
    user_detail = {}
    try:
        monthly_leave = []
        lms_user = LmsUser.objects.get(id=lms_user_id)
        user_detail.update({
            'full_name': lms_user.user.get_full_name(),
            'leaves': monthly_leave,
            })
        leaves = get_monthly_compensationLeave_detail_by_id_month(lms_user.id)
        for leave in leaves:
            monthly_leave.append({
                'days': leave.days,
                'id':leave.id,
                'leave_pending':leave.leave_pending,
                'leave_approved': leave.leave_approved
            })
        user_detail.update({
            'leaves': monthly_leave
        })
        return user_detail
    except (LmsUser.DoseNotExist, Exception) as e:
        print(e)
        return user_detail


def get_monthly_leave_detail_by_id_month(lms_user_id, month):
    leave_list = Leave.objects.order_by("-id").filter(from_date__month__gte = 4, user__id=lms_user_id)
    leave = []
    for leaves in leave_list:
        if leaves.from_date.month == 4:
            if (leaves.from_date.day<14 and leaves.to_date.day>=14) or leaves.from_date.day>=14:
                leave.append(leaves)
        else:
            leave.append(leaves)
    return leave


def get_monthly_compensationLeave_detail_by_id_month(lms_user_id):
    leave = CompensationLeave.objects.filter(user__id=lms_user_id)
    return leave


def get_monthly_leave_detail_of_all_user_by_month(month, user):
    # leave = Leave.objects.order_by("-id").filter(from_date__month=month)
    my_leave_approvees = LmsUser.objects.filter(leave_issuer=user)
    leave = Leave.objects.order_by("-id").filter(user__in=my_leave_approvees, from_date__month=month)
    return leave



def get_monthly_leave_detail_of_all_user_by_month(month, user):
    # leave = Leave.objects.order_by("-id").filter(from_date__month=month)
    my_leave_approvees = LmsUser.objects.filter(leave_issuer=user)
    leave = Leave.objects.order_by("-id").filter(user__in=my_leave_approvees, from_date__month=month)
    return leave


def get_monthly_compensationLeave_detail(lms_user_id, month):
    leave = Leave.objects.order_by("-id").filter(from_date__month=month, user__id=lms_user_id)
    return leave


def get_monthly_compensationLeave_detail_of_all_user(user):
    my_leave_approvees = LmsUser.objects.filter(leave_issuer=user)
    leave = CompensationLeave.objects.order_by("-id").filter(user__in=my_leave_approvees)
    return leave


def get_user_compensationLeave_detail(lms_user_id, user):
    user_detail = {}
    try:
        monthly_leave = []
        lms_user = LmsUser.objects.get(id=lms_user_id)
        if LmsUser.objects.filter(leave_issuer=user):
            leaves = get_monthly_compensationLeave_detail_of_all_user(user)
        else:
            leaves = get_monthly_compensationLeave_detail(lms_user_id)

        for leave in leaves:
            monthly_leave.append({
                'name':leave.user.user.get_full_name(),
                'days': leave.days,
                'id':leave.id,
                'leave_pending':leave.leave_pending,
                'leave_approved': leave.leave_approved
            })
        user_detail.update({
            'leaves': monthly_leave
        })

        return user_detail
    except (LmsUser.DoseNotExist, Exception) as e:
        print(e)
        return user_detail


def get_users_leaveDetailFor_searchEngine(my_leave_approvees,from_date,to_date):
    """
        Parameter
        ---------------------------------------------
        my_leave_approvees: gets logged in user object
        from_date: gets value from user input
        to_date: gets value from user input

        Loops and Conditions
        ----------------------------------------------
        for loop: gets all leave for requested user from from_date to to_date which is
        has already been approved

        if half day is apllied then 0.5 else 1

        if leave.user.user.get_full_name() in name_list: It checks if the fetched user has
        already been fetched before or not,
            If yes then adds the leaves days in total_days
            otherwise, add to list

        Return
        -------------------------------------------------
        It returns list of user excluding duplicated user

    """
    leave_issuer = LmsUser.objects.filter(leave_issuer=my_leave_approvees)
    name_list = {}
    total_days = 0
    for leave in Leave.objects.order_by("-id").filter(user__in=leave_issuer, from_date__gte=from_date, to_date__lte=to_date, leave_approved=True):
        leave_multiplier = 1
        if leave.half_day:
            leave_multiplier = 0.5
        total_days = ((leave.to_date - leave.from_date).days + 1) * leave_multiplier

        if leave.user.user.get_full_name() in name_list:
            name_list[leave.user.user.get_full_name()] = {
                'id': leave.user.user.id,
                'total_days': name_list[leave.user.user.get_full_name()]['total_days'] + total_days
            }
        else:
            name_list[leave.user.user.get_full_name()] = {
                'id':leave.user.user.id,
                'total_days':total_days
            }

    return name_list


def get_data(leave_of_lmsUser):
    data = []

    for leave in leave_of_lmsUser:
        multiplier = 1
        if leave.half_day:
            multiplier = 0.5

        data.append({
            'from':leave.from_date,
            'to':leave.to_date,
            'half_day':leave.half_day,
            'total_days': ((leave.to_date - leave.from_date).days + 1) * multiplier,
        })

    return data