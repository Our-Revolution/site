from django.contrib import admin

from .models import Nomination

# Register your models here.
@admin.register(Nomination)
class NominationAdmin(admin.ModelAdmin):
    list_display = ['group_name']
