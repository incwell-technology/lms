from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from lms_user import views as users_views
from leave_manager import urls as leave_manager_urls

urlpatterns = [
    path('login', users_views.user_login, name='user-login'),
    path('register', users_views.user_register, name='user-register'),
    path('logout', users_views.user_logout, name='user-logout'),
    path('password-change', users_views.change_password, name='password-change'),
    path('dashboard/', include(leave_manager_urls)),    
    path('', users_views.index, name='user-index'),
    path('password-reset', users_views.password_reset,name='password-reset'),
    path('password-reset/done', auth_views.PasswordResetDoneView.as_view(template_name = 'lms_user/password_reset_done.html'), name='password_reset_done'),
    path('reset/<token>/', users_views.password_reset_done, name='password_reset_confirm'),
    path('reset/done', auth_views.PasswordResetCompleteView.as_view(template_name='lms_user/password_reset_complete.html'), name='password_reset_complete'),
]
