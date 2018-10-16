from django.contrib import admin
from .models import OrganizingHubAccess, OrganizingHubFeatureAccess


class OrganizingHubFeatureAccessInline(admin.StackedInline):
    model = OrganizingHubFeatureAccess
    fields = ['feature']


@admin.register(OrganizingHubAccess)
class OrganizingHubAccessAdmin(admin.ModelAdmin):
    inlines = [OrganizingHubFeatureAccessInline]
    readonly_fields = [
        'date_created',
        'date_modified',
    ]
    fields = readonly_fields + ['local_group']
    # raw_id_fields = ['local_group']
