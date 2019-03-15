from django.conf.urls import url
from django.contrib import admin
from .admin_views import GroupLeaderSyncView
from .models import (
    LocalGroupAffiliation,
    LocalGroupProfile,
    LocalGroupRole,
    Group
)
from .forms import GisForm
from .actions import export_as_csv_action, geocode_groups


@admin.register(LocalGroupAffiliation)
class LocalGroupAffiliationAdmin(admin.ModelAdmin):
    list_filter = ['local_group_roles']
    raw_id_fields = ['local_group', 'local_group_profile']
    search_fields = ['local_group__name', 'local_group_profile__user__email']

    def get_urls(self):
        urls = super(LocalGroupAffiliationAdmin, self).get_urls()
        my_urls = [
            url(
                r'^group-leader-sync/',
                GroupLeaderSyncView.as_view(),
            ),
        ]
        return my_urls + urls


@admin.register(LocalGroupProfile)
class LocalGroupProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ['user']


@admin.register(LocalGroupRole)
class LocalGroupRoleAdmin(admin.ModelAdmin):
    filter_horizontal = ['permissions']


# Register your models here.
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'state',
        'city',
        'postal_code',
        'status',
        'signup_date',
        'group_id',
        'organizer',
        'signed_mou_version',
        'group_type',
        'group_rating',
    ]
    list_filter = [
        'status',
        'signed_mou_version',
        'organizer',
        'group_rating',
        'state',
    ]
    search_fields = ['name', 'state', 'city', 'group_id']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('issues',)
    form = GisForm
    actions = [export_as_csv_action("CSV Export"), geocode_groups]

    def get_actions(self, request):
        #Disable delete
        actions = super(GroupAdmin, self).get_actions(request)
        try:
            del actions['delete_selected']
        except KeyError:
            pass

        return actions

    def has_delete_permission(self, request, obj=None):
        #Disable delete
        return False
