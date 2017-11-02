from django import template
from pages.models import *

register = template.Library()

# Notification Banner snippet set to show
@register.inclusion_tag('pages/tags/notification-banner.html', takes_context=True)
def notification_banner(context):
    return {
        'notification_banner': NotificationBanner.objects.filter(show=True).first(),
        'request': context['request'],
    }
