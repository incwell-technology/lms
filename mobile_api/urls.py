from django.urls import path
from mobile_api import views as mobile_views

urlpatterns = [
    path('login', mobile_views.login, name="login"),
    path('holidays', mobile_views.holidays, name="holidays"),
    path('birthdays', mobile_views.birthday, name="birthdays"),
    path('leaves', mobile_views.leave, name="leaves"),
    path('users', mobile_views.users, name="users"),
    path('register', mobile_views.user_register, name="register"),
    path('leaves/create', mobile_views.create_leaves),
    path('leaves-request', mobile_views.get_leave_request),
    path('leaves-request/<int:id>', mobile_views.leave_approval_or_rejection),
    path('compensation/create', mobile_views.compensation_leave),
    path('compensation-request', mobile_views.get_compensation_request),
    path('compensation-request/<int:id>', mobile_views.compensation_approval_reject),
    path('leave-history', mobile_views.leaveHistory),
    path('leaves/report', mobile_views.generate_leave_report),
    path('leaves/report/<int:id>', mobile_views.leave_report_details),
    path('compensation/report', mobile_views.generate_compensationReport),
    path('compensation/report/<int:id>', mobile_views.compensationLeave_detail),
    path('generate-report-by-person/<int:id>', mobile_views.generate_report_byPerson),
    path('holidays/create',mobile_views.add_holiday),
    path('holidays/update/<int:id>',mobile_views.update_holiday),
    path('holidays/delete/<int:id>',mobile_views.delete_holiday),
    path('users/change-photo/<int:id>', mobile_views.change_user_photo),
    path('users/change-phone-number/<int:id>', mobile_views.change_user_phone_number),
    path('users/change-password', mobile_views.change_password),
    path('users/password-reset', mobile_views.password_reset),
    path('users/reset/<token>/', mobile_views.token_verify, name='verify_token'),
    path('users/password-reset-done/<int:pk>', mobile_views.password_reset_done),
    path('doc', mobile_views.doc),

]
