from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'state','city']
    list_filter = ['state','city','name']
    search_fields = ['name', 'state','city']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('issues',)
