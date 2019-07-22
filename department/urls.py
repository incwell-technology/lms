from django.urls import path
from department import views as dept_views

urlpatterns = [
    path('', dept_views.create_notice, name='notice'),
    path('view',dept_views.get_notice,name='notice-board')
]
