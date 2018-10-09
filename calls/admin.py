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
        'date_created',
        'date_modified',
    ]


@admin.register(CallCampaign)
class CallCampaignAdmin(admin.ModelAdmin):
    filter_horizontal = ['callers']
    form = CallCampaignAdminForm
    list_display = [
        'title',
        'local_group',
        'date_created',
        'status',
        'max_recipients',
        'state_or_territory',
        'postal_code',
        'max_distance',
    ]
    list_filter = ['status']
    readonly_fields = [
        'owner',
        'local_group',
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


@admin.register(CallProfile)
class CallProfileAdmin(admin.ModelAdmin):
    readonly_fields = ['user', 'date_created', 'date_modified']
