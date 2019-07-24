from django.shortcuts import render
from .models import Notice
from .forms import NoticeForm
from leave_manager.common.routes import get_formatted_routes, get_routes, is_leave_issuer
from django.urls import reverse
from django.http import HttpResponseRedirect
from mobile_api.common.fcm import fcm
from leave_manager.common import check_leave_admin

# Create your views here.

def create_notice(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))
    if not is_leave_issuer(request.user):
        return HttpResponseRedirect(reverse('leave_manager_dashboard'))
    
    context = {}
    routes = get_formatted_routes(get_routes(request.user), active_page = "notice")
    context.update({'routes':routes})
    
    if request.method == "POST":
        form = NoticeForm(request.POST)
        if form.is_valid():
            notice = form.save(commit=True)
            fcm(None,notice,"notice")
            return HttpResponseRedirect(reverse('notice-board'))
        else:
            form = NoticeForm()
            context.update({'form':form})
        return render(request, 'department/notice.html', context=context)
    else:
        form = NoticeForm()
        context.update({'form':form})

    return render(request, 'department/notice.html', context=context)



def get_notice(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))
    context = {}
    routes = get_formatted_routes(get_routes(request.user), active_page = "notice board")
    context.update({'routes':routes})
    notice = Notice.objects.all()
    context.update({'notices':notice})
    if check_leave_admin.is_leave_issuer(request.user):
        context.update({'leave_issuer':1})
    return render(request, 'department/noticeboard.html', context=context)


def delete_notice(request,id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user-login'))
    context = {}
    routes = get_formatted_routes(get_routes(request.user), active_page = "notice board")
    context.update({'routes':routes})
    notice = Notice.objects.all()
    context.update({'notices':notice})
    try:
        notice = Notice.objects.get(id=id)
        notice.delete()
    except (Notice.DoesNotExists, Exception) as e:
        print(e)
        context.update({'message':'Notice Not Deleted'})
        return render(request, 'department/noticeboard.html', context=context)
    return HttpResponseRedirect(reverse('notice-board'))
