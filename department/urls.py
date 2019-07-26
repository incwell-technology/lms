from django.urls import path
from department import views as dept_views

urlpatterns = [
    path('', dept_views.create_notice, name='notice'),
    path("delete/<int:id>", dept_views.delete_notice, name="notice-delete"),
    path('view',dept_views.get_notice,name='notice-board'),
]
