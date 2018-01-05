from django import template
from django.conf import settings
from pages.models import Group

register = template.Library()


@register.simple_tag
def bsd_create_account_url():
    return settings.BSD_CREATE_ACCOUNT_URL


@register.simple_tag
def bsd_reset_password_url():
    return settings.BSD_RESET_PASSWORD_URL


# Organizing Hub Navigation menu
@register.inclusion_tag('partials/group_portal_nav.html', takes_context=True)
def group_portal_nav(context):

    group = Group.objects.filter(
        rep_email__iexact=context['request'].user.email
    ).first()

    return {
        'group': group,
        'request': context['request'],
    }
