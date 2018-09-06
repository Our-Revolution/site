from django import template
from django.conf import settings
from local_groups.models import find_local_group_by_user
from organizing_hub.models import OrganizingHubLoginAlert

register = template.Library()

BSD_CREATE_ACCOUNT_URL = settings.BSD_CREATE_ACCOUNT_URL
ORGANIZING_DOCS_URL = settings.ORGANIZING_DOCS_URL
ORGANIZING_EMAIL = settings.ORGANIZING_EMAIL
ORGANIZING_GUIDES_URL = settings.ORGANIZING_GUIDES_URL
ORGANIZING_HUB_ADMINS_ENABLED = settings.ORGANIZING_HUB_ADMINS_ENABLED
ORGANIZING_HUB_CALL_SCRIPT_URL = settings.ORGANIZING_HUB_CALL_SCRIPT_URL
ORGANIZING_HUB_DASHBOARD_URL = settings.ORGANIZING_HUB_DASHBOARD_URL
ORGANIZING_HUB_PROMOTE_ENABLED = settings.ORGANIZING_HUB_PROMOTE_ENABLED


@register.simple_tag
def bsd_create_account_url():
    return BSD_CREATE_ACCOUNT_URL


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

    group = find_local_group_by_user(context['request'].user)

    return {
        'group': group,
        'request': context['request'],
    }


@register.simple_tag(takes_context=True)
def has_local_group_permission(context, local_group, permission):
    """
    Check if user has local group permission or not

    Parameters
    ----------
    permission : str
        Permission code

    Returns
        -------
        bool
            Return True if user has local group permission, otherwise False
    """

    """Check local group permissions"""
    has_permission = False
    user = context['request'].user
    if hasattr(user, 'localgroupprofile'):
        local_group_profile = user.localgroupprofile
        has_permission = local_group_profile.has_permission_for_local_group(
            local_group,
            permission
        )

    return has_permission


@register.simple_tag(takes_context=True)
def local_group(context):
    """TODO move to local groups template tags"""
    return find_local_group_by_user(context['request'].user)


# Organizing Hub Navigation menu
@register.inclusion_tag('partials/organizing_hub_nav.html', takes_context=True)
def organizing_hub_nav(context):

    group = find_local_group_by_user(context['request'].user)

    show_admins_link = ORGANIZING_HUB_ADMINS_ENABLED

    return {
        'group': group,
        'organizing_guides_url': ORGANIZING_GUIDES_URL,
        'organizing_docs_url': ORGANIZING_DOCS_URL,
        'show_admins_link': show_admins_link,
        'request': context['request'],
    }


@register.simple_tag
def organizing_email():
    return ORGANIZING_EMAIL


@register.simple_tag
def organizing_hub_call_script_url():
    return ORGANIZING_HUB_CALL_SCRIPT_URL


@register.simple_tag
def organizing_hub_dashboard_url():
    return ORGANIZING_HUB_DASHBOARD_URL


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
