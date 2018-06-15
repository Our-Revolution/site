from django import template
from django.conf import settings
from organizing_hub.models import OrganizingHubLoginAlert

register = template.Library()


@register.simple_tag
def event_url(event_id_obfuscated):
    return "%s/page/event/detail/%s" % (
        settings.BSD_BASE_URL,
        event_id_obfuscated
    )


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
