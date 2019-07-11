from django.urls import path, include
from lms_user import views as users_views
from leave_manager import urls as leave_manager_urls

urlpatterns = [
    path('login', users_views.user_login, name='user-login'),
    path('register', users_views.user_register, name='user-register'),
    path('logout', users_views.user_logout, name='user-logout'),
    path('dashboard/', include(leave_manager_urls)),
    path('', users_views.index, name='user-index'),
]
