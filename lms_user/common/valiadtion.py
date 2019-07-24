from datetime import datetime,timedelta


def register_validation(request, context):
    if len(request.POST['first_name'])<2 or len(request.POST['first_name'])>50 or len(request.POST['last_name'])<2 or len(request.POST['last_name'])>50:
        context.update({'message': 'First and Last name should not be less than 2 and greater than 50'})
        return context
    if len(request.POST['phone_number']) < 7 or len(request.POST['phone_number'])>15:
        context.update({'message': 'Invalid Phone Number.Phone number should not be less than 7 and greater than 15'})
        return context
    if request.POST['date_of_birth'] > str(datetime.today()) or request.POST['date_of_birth'] < str(datetime.today() - timedelta(days=365*65)):
        context.update({'message': 'Invalid Date of Birth'})
        return context
    if request.POST['joined_date'] > str(datetime.today()):
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

