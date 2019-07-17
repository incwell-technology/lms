import calendar
from datetime import datetime
from lms_user.models import LmsUser
from django.urls import reverse_lazy
from leave_manager.models import Leave, Holiday, CompensationLeave
from leave_manager.common.send_email_notification import send_email_notification
from leave_manager.common.user_image import get_image_url


def apply_leave(**kwargs):
    leave_details = kwargs['leave_details']
    request = kwargs['request']
    try:
        leave = Leave.objects.create(
            type=leave_details['leave_type'],
            from_date=leave_details['from_date'],
            to_date=leave_details['to_date'],
            half_day=leave_details['half_day'],
            reason=leave_details['leave_reason'],
            user=leave_details['user']
        )
        update_details = {
            'recipient_email': leave_details['issuer'].email,
            'email_subject': 'LMS | A new Leave Request Has Arrived ',
            'email_body': '''
                    Hi {}, A new leave Request has arrived.
                    From: {}
                    Leave Type: {}
                    Half Day: {}
                    Days: {}
                    Leave Reason: {}
                    URL: {}
                    '''.format(leave_details['issuer'].get_full_name(), leave_details['user'].user.get_full_name(),
                               leave_details['leave_type'],
                               leave_details['half_day'],
                               ((leave_details['to_date'] - leave_details['from_date']).days + 1) * leave_details[
                                                             'leave_multiplier'],
                               leave_details['leave_reason'],
                               'http://{}{}'.format(request.META['HTTP_HOST'],
                                                    reverse_lazy('leave_manager_leave_requests')))
        }
        if send_email_notification(update_details=update_details):
            return True
        else:
            leave.delete()
            return False
    except Exception as e:
        print(e)
        return False


def half_leave_applied(request):
    try:
        if int(request.POST['half_leave']) == 1:
            return True
    except Exception as e:
        print(e)
        return False
    return False


def get_leave_requests_by_id(user, id):
    pending_leave_requests = []
    my_leave_approvees = LmsUser.objects.filter(leave_issuer=user)
    for leave_request in Leave.objects.filter(user__in=my_leave_approvees, leave_pending=True, id=id):
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
            }
        )
    return pending_leave_requests


def get_leave_requests(user):
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


def get_leave_today():
    leaves_today = []
    for leave_request in Leave.objects.filter(from_date__lte=datetime.today(), to_date__gte=datetime.today(),
                                              leave_pending=False, leave_approved=True):
        leaves_today.append({
            'id': leave_request.id,
            'full_name': leave_request.user.user.get_full_name(),
            'department': leave_request.user.department.department,
            'from_date': str(leave_request.from_date),
            'to_date': str(leave_request.to_date),
            'leave_type': leave_request.type.type,
            'leave_reason': leave_request.reason,
            'half_day': leave_request.half_day,
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


def get_leave_count_monthly(leave, month):
    if leave.from_date.month == leave.to_date.month:
        return leave.to_date.day - leave.from_date.day + 1
    elif leave.from_date.month == month:
        return calendar.monthrange(leave.from_date.year, leave.from_date.month)[1] - leave.from_date.day + 1
    else:
        return leave.to_date.day


def get_user_leave_detail_monthly(lms_user_id, month, user):
    user_detail = {}
    try:
        monthly_leave = []
        lms_user = LmsUser.objects.get(id=lms_user_id)
        user_detail.update({
            'full_name': lms_user.user.get_full_name(),
            'leaves': monthly_leave,
            })

        if LmsUser.objects.filter(leave_issuer=user):
            leaves = get_monthly_leave_detail_of_all_user_by_month(month, user)
        else:
            leaves = get_monthly_leave_detail_by_id_month(lms_user_id,month)

        for leave in leaves:
            monthly_leave.append({
                'name':leave.user,
                'leave_type': leave.type.type,
                'from_date': leave.from_date,
                'to_date': leave.to_date,
                'days': get_leave_count_monthly(leave, month),
                'id':leave.id,
                'leave_pending':leave.leave_pending,
                'leave_approved': leave.leave_approved
            })
        user_detail.update({
            'leaves': monthly_leave
        })

        return user_detail
    except Exception as e:
        print(e)
        return user_detail

def get_own_leave_detail_monthly(lms_user_id, month):
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
                'name':leave.user,
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
    except Exception as e:
        print(e)
        return user_detail


def approve_leave_request(request, leave_id):
    try:
        leave = Leave.objects.get(id=leave_id)
        leave.leave_pending = False
        leave.leave_approved = True
        leave_detail = get_leave_detail(leave)
        user = leave_detail['lms_user']
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
        update_details = {
            'recipient_email': user.user.email,
            'email_subject': 'LMS | Your Leave Request Has Been Approved',
            'email_body': '''
            Hi {}, Your Leave Request Has just been approved by {}.
            Leave Type: {}
            Half Leave: {}
            Days: {}
            Leave Reason {}
            '''.format(user.user.get_full_name(), request.user.get_full_name(), leave_detail['leave_type'],
                       leave_detail['half_day'],
                       leave_detail['total_days'], leave_detail['leave_reason'])
        }
        user.save()
        leave.save()
        if send_email_notification(update_details=update_details):
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False

def reject_leave_request(request, leave_id):
    try:
        leave = Leave.objects.get(id=leave_id)
        leave_detail = get_leave_detail(leave)
        user = leave_detail['lms_user']
        leave.leave_pending = False
        leave.leave_approved = False
        update_details = {
            'recipient_email': user.user.email,
            'email_subject': 'LMS | Your Leave Request Has Been Rejected',
            'email_body': '''
                    Hi {}, Your Leave Request Has just been rejected by {}.
                    Leave Type: {}
                    Half Leave: {}
                    Days: {}
                    Leave Reason {}
                    '''.format(user.user.get_full_name(), request.user.get_full_name(), leave_detail['leave_type'],
                               leave_detail['half_day'],
                               leave_detail['total_days'], leave_detail['leave_reason'])
        }

        leave.save()
        
        if send_email_notification(update_details=update_details):
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


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

def get_monthly_compensationLeave_detail(lms_user_id, month):
    leave = Leave.objects.order_by("-id").filter(from_date__month=month, user__id=lms_user_id)
    return leave


def get_monthly_leave_detail_of_all_user_by_month(month, user):
    # leave = Leave.objects.order_by("-id").filter(from_date__month=month)
    my_leave_approvees = LmsUser.objects.filter(leave_issuer=user)
    leave = Leave.objects.order_by("-id").filter(user__in=my_leave_approvees, from_date__month=month)
    return leave

def get_monthly_compensationLeave_detail_of_all_user(user):
    my_leave_approvees = LmsUser.objects.filter(leave_issuer=user)
    leave = CompensationLeave.objects.order_by("-id").filter(user__in=my_leave_approvees)
    return leave

def get_holidays(request):
    holidays = Holiday.objects.all()
    company_holidays = []
    for holiday in holidays:
        image_url = get_image_url(None,request,'holiday',holiday.id)
        company_holidays.append({
            'id':holiday.id,
            'title':holiday.title,
            'from_date':holiday.from_date,
            'to_date':holiday.to_date,
            'description':holiday.description,
            'image':image_url,
            'days': get_totalDays_ofEach_holidays(holiday.from_date,holiday.to_date)
        })
    return company_holidays


def get_totalDays_ofEach_holidays(from_date,to_date):
    delta = to_date-from_date
    return delta.days+1

def get_all_leaves_unseen():
    leave = Leave.objects.filter(notification=True).count()
    return leave

def apply_CompensationLeave(**kwargs):
    leave_details = kwargs['leave_details']
    request = kwargs['request']
    try:
        leave = CompensationLeave.objects.create(
            reason=leave_details['leave_reason'],
            days = leave_details['days'],
            user=leave_details['user']
        )
        update_details = {
            'recipient_email': leave_details['issuer'].email,
            'email_subject': 'LMS | A new Leave Request Has Arrived ',
            'email_body': '''
                    Hi {}, A new compensation leave Request has arrived.
                    From: {}
                    Leave Reason: {}
                    Days: {}
                    URL: {}
                    '''.format(leave_details['issuer'].get_full_name(), leave_details['user'].user.get_full_name(),
                               leave_details['leave_reason'], leave_details['days'],
                               'http://{}{}'.format(request.META['HTTP_HOST'],
                                                    reverse_lazy('leave_manager_leave_requests')))
        }
        if send_email_notification(update_details=update_details):
            return True
        else:
            leave.delete()
            return False
    except Exception as e:
        print(e)
        return False


def get_compensationLeave_requests(user):
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


def get_compensationLeave_requests_by_id(user, id):
    pending_leave_requests = []
    my_leave_approvees = LmsUser.objects.filter(leave_issuer=user)
    for leave_request in CompensationLeave.objects.filter(user__in=my_leave_approvees, leave_pending=True, id=id):
        pending_leave_requests.append(
            {
                'id': leave_request.id,
                'full_name': leave_request.user.user.get_full_name(),
                'department': leave_request.user.department.department,
                'days': leave_request.days,
                'leave_reason': leave_request.reason,
            }
        )
    return pending_leave_requests


def reject_compensationLeave_request(request, leave_id):
    try:
        leave = CompensationLeave.objects.get(id=leave_id)
        leave_detail = get_compensationLeave_detail(leave)
        user = leave_detail['lms_user']
        leave.leave_pending = False
        leave.leave_approved = False
        update_details = {
            'recipient_email': user.user.email,
            'email_subject': 'LMS | Your Compensation Leave Request Has Been Rejected',
            'email_body': '''
                    Hi {}, Your Leave Request Has just been rejected by {}.
                    Days: {}
                    Leave Reason: {}
                    '''.format(user.user.get_full_name(), request.user.get_full_name(), 
                               leave_detail['days'], leave_detail['leave_reason'])
        }
        leave.save()
        
        if send_email_notification(update_details=update_details):
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False

def get_compensationLeave_detail(leave):
    try:
        leave_detail = {
            'id': leave.id,
            'lms_user': leave.user,
            'department': leave.user.department.department,
            'days': leave.days,
            'leave_reason': leave.reason,
        }
        return leave_detail
    except Exception as e:
        print('Could not Get Compensation Leave Detail', e)
        return {}


def approve_compensationLeave_request(request, leave_id):
    try:
        leave = CompensationLeave.objects.get(id=leave_id)
        leave.leave_pending = False
        leave.leave_approved = True
        leave_detail = get_compensationLeave_detail(leave)
        user = leave_detail['lms_user']
        user.compensation_leave += leave_detail['days']
           
        update_details = {
            'recipient_email': user.user.email,
            'email_subject': 'LMS | Your Compensation Leave Request Has Been Approved',
            'email_body': '''
            Hi {}, Your Leave Request Has just been approved by {}.
            Days: {}
            Leave Reason {}
            '''.format(user.user.get_full_name(), request.user.get_full_name(),
                       leave_detail['days'], leave_detail['leave_reason'])
        }
        user.save()
        leave.save()
        if send_email_notification(update_details=update_details):
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


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
                'name':leave.user,
                'days': leave.days,
                'id':leave.id,
                'leave_pending':leave.leave_pending,
                'leave_approved': leave.leave_approved
            })
        user_detail.update({
            'leaves': monthly_leave
        })

        return user_detail
    except Exception as e:
        print(e)
        return user_detail


def get_monthly_compensationLeave_detail_by_id_month(lms_user_id):
    leave = CompensationLeave.objects.filter(user__id=lms_user_id)
    return leave


def get_user_compensationLeave_detail(lms_user_id, user):
    user_detail = {}
    try:
        monthly_leave = []
        lms_user = LmsUser.objects.get(id=lms_user_id)
        user_detail.update({
            'full_name': lms_user.user.get_full_name(),
            'leaves': monthly_leave,
            })

        if LmsUser.objects.filter(leave_issuer=user):
            leaves = get_monthly_compensationLeave_detail_of_all_user(user)
        else:
            leaves = get_monthly_compensationLeave_detail(lms_user_id)

        for leave in leaves:
            monthly_leave.append({
                'name':leave.user,
                'days': leave.days,
                'id':leave.id,
                'leave_pending':leave.leave_pending,
                'leave_approved': leave.leave_approved
            })
        user_detail.update({
            'leaves': monthly_leave
        })

        return user_detail
    except Exception as e:
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
        print(leave)
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
