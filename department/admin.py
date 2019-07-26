from django.contrib import admin
from department import models as dept_models


# Register your models here.

@admin.register(dept_models.Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department',)


@admin.register(dept_models.Notice)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('topic',)