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
        'date_submitted',
        'date_sent',
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
    ]
    list_display_links = list_display
    list_filter = ['status']
    raw_id_fields = ['contact_list']
