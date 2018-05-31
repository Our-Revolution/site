from django import template
from django.conf import settings
from pages.models import *

register = template.Library()


@register.simple_tag
def add_group_url():
    return settings.ADD_GROUP_URL


@register.simple_tag
def base_url():
    return settings.BASE_URL


@register.simple_tag
def candidates_url():
    return settings.CANDIDATES_URL


@register.simple_tag
def or_address():
    return '%s %s, %s %s' % (
        settings.OR_ADDRESS_STREET,
        settings.OR_ADDRESS_CITY,
        settings.OR_ADDRESS_STATE,
        settings.OR_ADDRESS_ZIP
    )


@register.simple_tag
def or_address_city():
    return settings.OR_ADDRESS_CITY


@register.simple_tag
def or_address_state():
    return settings.OR_ADDRESS_STATE


@register.simple_tag
def or_address_street():
    return settings.OR_ADDRESS_STREET


@register.simple_tag
def or_address_zip():
    return settings.OR_ADDRESS_ZIP


@register.simple_tag(takes_context=True)
def or_meta_image_url(context):
    request = context['request']
    absolute_url = request.build_absolute_uri(settings.OR_META_IMAGE_URL)
    return absolute_url


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


@register.simple_tag
def start_group_url():
    return settings.START_GROUP_URL
