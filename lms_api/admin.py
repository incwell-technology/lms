from django.contrib import admin
from lms_api.models import APIToken


# Register your models here.
@admin.register(APIToken)
class APITokenAdmin(admin.ModelAdmin):
    list_display = ('user',)
