from django.conf.urls import url
from django.contrib import admin
from .admin_views import GroupLeaderSyncView
from local_groups.models import LocalGroupAffiliation


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
