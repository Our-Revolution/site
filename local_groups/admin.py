from django.contrib import admin
from .models import *
from .forms import GisForm
from .actions import export_as_csv_action

# Register your models here.
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'state','city','country','status']
    list_filter = ['status','state']
    search_fields = ['name', 'state','city']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('issues',)
    form = GisForm
    actions = [export_as_csv_action("CSV Export")]
    
    def has_delete_permission(self, request, obj=None):
        return False
