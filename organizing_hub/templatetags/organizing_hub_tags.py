from django import template
from django.conf import settings
from local_groups.models import get_local_group_for_user
from organizing_hub.models import OrganizingHubLoginAlert

register = template.Library()

ORGANIZING_HUB_PROMOTE_ENABLED = settings.ORGANIZING_HUB_PROMOTE_ENABLED
ORGANIZING_HUB_ADMINS_ENABLED = settings.ORGANIZING_HUB_ADMINS_ENABLED


@register.simple_tag
def bsd_create_account_url():
    return settings.BSD_CREATE_ACCOUNT_URL


@register.inclusion_tag('partials/events_nav.html', takes_context=True)
def events_nav(context):

    """Show Hydra Promote Link if Hub Promote is not enabled"""
    show_promote_link = not ORGANIZING_HUB_PROMOTE_ENABLED

    return {
        'show_promote_link': show_promote_link,
        'request': context['request'],
    }


# Organizing Hub templates
@register.inclusion_tag('partials/group_link.html', takes_context=True)
def group_link(context):

    group = get_local_group_for_user(context['request'].user)

    return {
        'group': group,
        'request': context['request'],
    }


# Organizing Hub Navigation menu
@register.inclusion_tag('partials/organizing_hub_nav.html', takes_context=True)
def organizing_hub_nav(context):

    group = get_local_group_for_user(context['request'].user)

    show_admins_link = ORGANIZING_HUB_ADMINS_ENABLED

    return {
        'group': group,
        'organizing_guides_url': settings.ORGANIZING_GUIDES_URL,
        'organizing_docs_url': settings.ORGANIZING_DOCS_URL,
        'show_admins_link': show_admins_link,
        'request': context['request'],
    }


@register.simple_tag
def organizing_email():
    return settings.ORGANIZING_EMAIL


@register.simple_tag
def organizing_hub_dashboard_url():
    return settings.ORGANIZING_HUB_DASHBOARD_URL


@register.inclusion_tag(
    'organizing_hub/tags/organizing_hub_login_alert.html',
    takes_context=True
)
def organizing_hub_login_alert(context):
    """Organizing Hub Login Alert snippet set to show"""
    return {
        'organizing_hub_login_alert': OrganizingHubLoginAlert.objects.filter(
            show=True
        ).first(),
        'request': context['request'],
    }
