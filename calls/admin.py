from django.contrib import admin
from .models import Call, CallCampaign, CallProfile, CallResponse


class CallResponseInline(admin.StackedInline):
    readonly_fields = ['date_created', 'date_modified']
    fields = readonly_fields + [
        'question',
        'answer',
    ]
    model = CallResponse


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
    readonly_fields = [
        'owner',
        'local_group',
        'contact_list',
        'date_created',
        'date_modified',
    ]
    fields = readonly_fields + [
        'status',
        'title',
        'script',
        'postal_code',
        'max_distance',
        'max_recipients',
        'callers',
    ]


@admin.register(CallProfile)
class CallProfileAdmin(admin.ModelAdmin):
    readonly_fields = ['user', 'date_created', 'date_modified']
