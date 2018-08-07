from django.contrib import admin
from .models import Call, CallCampaign, CallProfile, CallResponse


@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    pass


@admin.register(CallCampaign)
class CallCampaignAdmin(admin.ModelAdmin):
    filter_horizontal = ['callers']
    readonly_fields = [
        'owner',
        'local_group',
        'contact_list',
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
    pass


@admin.register(CallResponse)
class CallResponseAdmin(admin.ModelAdmin):
    readonly_fields = ['call', 'date_created']
    fields = readonly_fields + [
        'question',
        'answer',
    ]
