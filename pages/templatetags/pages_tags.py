from django import template
from pages.models import *

register = template.Library()

# Notification Banner snippet
@register.inclusion_tag('pages/tags/notification_banner.html', takes_context=True)
def notification_banner(context):
    # TODO: return only one item instead of all objects
    return {
        'notification_banner': NotificationBanner.objects.all(),
        'request': context['request'],
    }
