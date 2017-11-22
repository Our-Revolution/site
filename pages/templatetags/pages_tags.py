from django import template
from django.conf import settings
from pages.models import *

register = template.Library()

# Navigation menu
@register.inclusion_tag('partials/nav.html', takes_context=True)
def navigation_menu(context):
    return {
        'shop_nav_enabled': settings.SHOP_NAV_ENABLED,
        'request': context['request'],
    }

# Notification Banner snippet set to show
@register.inclusion_tag('pages/tags/notification_banner.html', takes_context=True)
def notification_banner(context):
    return {
        'notification_banner': NotificationBanner.objects.filter(show=True).first(),
        'request': context['request'],
    }
