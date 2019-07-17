from django.contrib import admin
from leave_rhymes.models import Rhyme, RhymeType


# Register your models here.

@admin.register(Rhyme)
class RhymeAdmin(admin.ModelAdmin):
    list_display = ('title',)


@admin.register(RhymeType)
class RhymeTypeAdmin(admin.ModelAdmin):
    list_display = ('type',)
