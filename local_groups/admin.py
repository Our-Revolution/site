from django.contrib import admin
from .models import *
from .forms import GisForm
from .actions import export_as_csv_action, geocode_groups

# Register your models here.
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'state','city','postal_code','status','signup_date','group_id','organizer','signed_mou_version']
    list_filter = ['status','signed_mou_version','organizer','state']
    search_fields = ['name', 'state','city','group_id']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('issues',)
    form = GisForm
    actions = [export_as_csv_action("CSV Export")]
    
    def get_actions(self, request):
        #Disable delete
        actions = super(GroupAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        #Disable delete
        return False
