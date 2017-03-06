from django.contrib import admin
from .models import *
from .widgets import LatLongWidget
from django.contrib.gis.db import models as geomodels

# Register your models here.
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'state','city']
    list_filter = ['state','city','name']
    search_fields = ['name', 'state','city']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('issues',)
    formfield_overrides = {
        geomodels.PointField: {'widget': LatLongWidget}
    }
