from django.contrib import admin
from department.models import Department


# Register your models here.

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department',)
