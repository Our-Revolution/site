from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def organizing_hub_dashboard_url():
    return settings.ORGANIZING_HUB_DASHBOARD_URL
