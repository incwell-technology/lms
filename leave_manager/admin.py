from django.contrib import admin
from leave_manager import models as leave_models


# Register your models here.
@admin.register(leave_models.LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('type',)


@admin.register(leave_models.Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('type', 'from_date', 'to_date')
