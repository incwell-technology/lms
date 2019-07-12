from django.urls import path
from lms_api import views as api_views

urlpatterns = [
    path('', api_views.index_view, name='lms_api_index'),
    path('leaves', api_views.leave_view, name='lms_api_leaves'),
    path('birthdays', api_views.birthday_view, name='lms_api_birthdays'),
    path('leavesMonthly', api_views.monthly_detail_view, name='lms_api_monthly_user_leaves'),
    path('rhymesNoLeave', api_views.no_leave_rhyme_view, name='lms_api_no_leaves_rhymes'),
    path('rhymesAllHands', api_views.all_hands_rhyme_view, name='lms_api_all_hands_rhymes'),
    path('companyHolidays', api_views.company_holidays, name='lms_api_company_holidays'),
]
