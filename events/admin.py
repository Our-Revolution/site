from django.contrib import admin
from .forms import EventPromotionAdminForm
from .models import EventPromotion


@admin.register(EventPromotion)
class EventPromotionAdmin(admin.ModelAdmin):
    readonly_fields = [
        'event_name',
        'event_external_id',
        'user_external_id',
        'contact_list',
        'get_list_status',
        'get_list_size',
        'date_submitted',
        'date_sent',
        'sent_count',
        'success_rate',
    ]
    fields = readonly_fields + [
        'status',
        'sender_display_name',
        'subject',
        'message',
        'max_recipients',
    ]
    form = EventPromotionAdminForm
    list_display = [
        'id',
        'event_name',
        'event_external_id',
        'user_external_id',
        'max_recipients',
        'date_submitted',
        'status',
        'date_sent',
        'success_rate',
    ]
    list_display_links = list_display
    list_filter = ['status']
    raw_id_fields = ['contact_list']

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
