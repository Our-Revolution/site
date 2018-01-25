from django import template
from django.conf import settings
from pages.models import *

register = template.Library()


@register.simple_tag
def candidates_url():
    return settings.CANDIDATES_URL


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


@register.simple_tag
def results_url():
    return settings.RESULTS_URL


@register.simple_tag
def results_2016_url():
    return settings.RESULTS_2016_URL


@register.simple_tag
def results_2017_url():
    return settings.RESULTS_2017_URL
