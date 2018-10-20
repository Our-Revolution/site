from django.contrib import admin
from .models import OrganizingHubAccess, OrganizingHubFeatureAccess


class OrganizingHubFeatureAccessInline(admin.StackedInline):
    model = OrganizingHubFeatureAccess
    fields = ['feature']


@admin.register(OrganizingHubAccess)
class OrganizingHubAccessAdmin(admin.ModelAdmin):
    inlines = [OrganizingHubFeatureAccessInline]
    list_display = [
        'id',
        'get_group_name',
        'get_group_state',
        'get_group_city',
        'get_group_postal_code',
        'get_group_slug',
        'get_group_status',
        'date_modified',
    ]
    list_display_links = list_display
    list_filter = [
        'local_group__status',
        'local_group__state',
    ]
    readonly_fields = [
        'date_created',
        'date_modified',
    ]
    fields = readonly_fields + ['local_group']
    raw_id_fields = ['local_group']
    search_fields = [
        'id',
        'local_group__city',
        'local_group__name',
        'local_group__group_id',
        'local_group__slug',
        'local_group__state',
        'local_group__postal_code',
    ]

    def get_group_city(self, obj):
        return obj.local_group.city

    get_group_city.short_description = 'City'

    def get_group_name(self, obj):
        return obj.local_group.name

    get_group_name.short_description = 'Local Group'

    def get_group_postal_code(self, obj):
        return obj.local_group.postal_code

    get_group_postal_code.short_description = 'Postal'

    def get_group_slug(self, obj):
        return obj.local_group.slug

    get_group_slug.short_description = 'Slug'

    def get_group_status(self, obj):
        return obj.local_group.get_status_display()

    get_group_status.short_description = 'Status'

    def get_group_state(self, obj):
        return obj.local_group.get_state_display()

    get_group_state.short_description = 'State'
