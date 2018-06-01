from django.conf.urls import url
from django.contrib import admin
from django.http import HttpResponseRedirect
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

    def get_urls(self):
        urls = super(LocalGroupAffiliationAdmin, self).get_urls()
        my_urls = [
            url(
                r'^group-leader-sync/',
                GroupLeaderSyncView.as_view(),
            ),
        ]
        return my_urls + urls

    def go_to_group_leader_sync(self, request, queryset):
        return HttpResponseRedirect(
            "/admin/local_groups/localgroupaffiliation/group-leader-sync/"
        )

    actions = [
        # go_to_group_leader_sync("CSV Export"),
        'go_to_group_leader_sync',
        # 'set_to_needs_staff_review',
        # 'set_to_under_review',
        # 'set_to_approved',
        # 'set_to_removed',
        # 'set_to_expired',
        # 'go_to_group_leader_sync',
    ]


@admin.register(LocalGroupProfile)
class LocalGroupProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(LocalGroupRole)
class LocalGroupRoleAdmin(admin.ModelAdmin):
    pass


# Register your models here.
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'state', 'city', 'postal_code', 'status', 'signup_date',
        'group_id', 'organizer', 'signed_mou_version', 'group_type'
    ]
    list_filter = ['status', 'signed_mou_version', 'organizer', 'state']
    search_fields = ['name', 'state', 'city', 'group_id']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('issues',)
    form = GisForm
    actions = [export_as_csv_action("CSV Export"), geocode_groups]

    def get_actions(self, request):
        #Disable delete
        actions = super(GroupAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        #Disable delete
        return False
