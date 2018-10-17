from django.contrib import admin
from .forms import CallCampaignAdminForm
from .models import Call, CallCampaign, CallProfile, CallResponse


class CallResponseInline(admin.StackedInline):
    model = CallResponse
    readonly_fields = ['date_created', 'date_modified']
    fields = readonly_fields + [
        'question',
        'answer',
    ]


@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    inlines = [CallResponseInline]
    readonly_fields = [
        'call_campaign',
        'caller',
        'contact',
        'uuid',
        'date_created',
        'date_modified',
    ]


@admin.register(CallCampaign)
class CallCampaignAdmin(admin.ModelAdmin):
    filter_horizontal = ['callers']
    form = CallCampaignAdminForm
    list_display = [
        'id',
        'title',
        'local_group',
        'state_or_territory',
        'postal_code',
        'max_recipients',
        'status',
        'get_list_status',
        'get_list_size',
        'date_created',
    ]
    list_display_links = list_display
    list_filter = ['status', 'state_or_territory']
    readonly_fields = [
        'owner',
        'local_group',
        'get_list_status',
        'get_list_size',
        'point',
        'date_created',
        'date_modified',
    ]
    fields = readonly_fields + [
        'title',
        'status',
        'contact_list',
        'script',
        'state_or_territory',
        'postal_code',
        'max_distance',
        'max_recipients',
        'callers',
    ]
    raw_id_fields = ['callers', 'contact_list']
    search_fields = [
        'id',
        'local_group__name',
        'local_group__group_id',
        'local_group__slug',
        'postal_code',
        'state_or_territory',
        'title',
    ]

    def get_list_size(self, obj):
        contact_list = obj.contact_list
        if contact_list is not None:
            return contact_list.contacts.count()
        else:
            return None

    get_list_size.short_description = 'List Size'

    def get_list_status(self, obj):
        contact_list = obj.contact_list
        if contact_list is not None:
            return contact_list.get_status_display()
        else:
            return None

    get_list_status.short_description = 'List Status'


@admin.register(CallProfile)
class CallProfileAdmin(admin.ModelAdmin):
    readonly_fields = ['user', 'date_created', 'date_modified']
