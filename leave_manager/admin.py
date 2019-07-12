from django.contrib import admin
from leave_manager import models as leave_models


# Register your models here.
@admin.register(leave_models.LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('type',)


@admin.register(leave_models.Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'from_date', 'to_date', 'half_day', 'leave_approved', 'leave_pending')

@admin.register(leave_models.Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('title', 'from_date','to_date','description')

@admin.register(leave_models.CompensationLeave)
class CompensationLeave(admin.ModelAdmin):
    list_display = ('user','days')


# @admin.register(leave_models.LeaveStatus)
# class LeaveStatusAdmin(admin.ModelAdmin):
#     list_display = ('status',)
