from django import template
from django.conf import settings
from nominations.models import *

register = template.Library()


# Nominations Platform Alert snippet set to show
@register.inclusion_tag(
    'nominations/tags/nominations_platform_alert.html',
    takes_context=True
)
def nominations_platform_alert(context):
    return {
        'nominations_platform_alert': NominationsPlatformAlert.objects.filter(
            show=True
        ).first(),
        'request': context['request'],
    }
