from django import template
from pages.models import *

register = template.Library()

# Notification Banner snippets that are set to show
@register.inclusion_tag('pages/tags/notification-banner.html', takes_context=True)
def notification_banner(context):
    return {
        'notifications': NotificationBanner.objects.filter(show=True),
        'request': context['request'],
    }
