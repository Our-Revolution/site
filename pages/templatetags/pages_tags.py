from django import template
from django.conf import settings
from pages.models import AlertLevels, NotificationBanner, SplashModal

register = template.Library()

BASE_URL = settings.BASE_URL
GOOGLE_MAPS_PUBLIC_KEY = settings.GOOGLE_MAPS_PUBLIC_KEY
OR_META_IMAGE_URL = settings.OR_META_IMAGE_URL
SPLASH_COOKIE_EXPIRE_DAYS = settings.SPLASH_COOKIE_EXPIRE_DAYS
SPLASH_COOKIE_NAME = settings.SPLASH_COOKIE_NAME
SPLASH_COOKIE_SECURE = settings.SPLASH_COOKIE_SECURE
SPLASH_DONATE_URL_DEFAULT = settings.SPLASH_DONATE_URL_DEFAULT
SPLASH_MODAL_ENABLED = settings.SPLASH_MODAL_ENABLED


@register.simple_tag
def add_group_url():
    return settings.GROUPS_ADD_URL


@register.simple_tag
def base_url():
    return BASE_URL


@register.simple_tag
def candidates_url():
    return settings.CANDIDATES_URL


@register.simple_tag
def endorsement_process_url():
    return settings.ENDORSEMENT_PROCESS_URL


@register.simple_tag
def get_alert_level_class(value):
    """Pass in alert level value and get back approporiate CSS class."""
    classes_dict = {
        AlertLevels.success.value[0]: 'success',
        AlertLevels.info.value[0]: 'info',
        AlertLevels.warning.value[0]: 'warning',
        AlertLevels.danger.value[0]: 'danger'
    }
    return classes_dict[value]


@register.simple_tag
def groups_url():
    return settings.GROUPS_URL


@register.simple_tag
def google_maps_public_key():
    return GOOGLE_MAPS_PUBLIC_KEY


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
    """If context request is not available use base url"""
    try:
        request = context['request']
        absolute_url = request.build_absolute_uri(OR_META_IMAGE_URL)
    except KeyError:
        absolute_url = BASE_URL + OR_META_IMAGE_URL
    return absolute_url


# Navigation menu
@register.inclusion_tag('partials/nav.html', takes_context=True)
def navigation_menu(context):
    """If context request is not available use empty string for path"""
    try:
        request = context['request']
        request_path = request.path
    except KeyError:
        request_path = ''
    return {
        'shop_nav_enabled': settings.SHOP_NAV_ENABLED,
        'request_path': request_path,
    }


# Notification Banner snippet set to show
@register.inclusion_tag('pages/tags/notification_banner.html', takes_context=True)
def notification_banner(context):
    return {
        'notification_banner': NotificationBanner.objects.filter(
            show=True
        ).first(),
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
def results_2018_url():
    return settings.RESULTS_2018_URL


# Splash modal
@register.inclusion_tag('pages/tags/splash_modal.html', takes_context=True)
def splash_modal(context):
    """Get splash modal if feature is enabled"""
    if SPLASH_MODAL_ENABLED:
        splash_modal = SplashModal.objects.filter(show=True).first()
    else:
        splash_modal = None

    if splash_modal is not None and splash_modal.donate_url is not None:
        donate_url = splash_modal.donate_url
    else:
        donate_url = SPLASH_DONATE_URL_DEFAULT

    if splash_modal is not None:
        url_param_recurring = '1' if splash_modal.donate_recurring else '0'
    else:
        url_param_recurring = '0'

    return {
        'donate_url': donate_url,
        'splash_modal': splash_modal,
        'url_param_recurring': url_param_recurring,
    }


@register.simple_tag
def splash_cookie_expire_days():
    return SPLASH_COOKIE_EXPIRE_DAYS


@register.simple_tag
def splash_cookie_name():
    return SPLASH_COOKIE_NAME


@register.simple_tag
def splash_cookie_secure():
    return SPLASH_COOKIE_SECURE


@register.simple_tag
def start_group_url():
    return settings.START_GROUP_URL
