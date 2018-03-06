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


@register.simple_tag
def event_create_enabled():
    return settings.EVENT_CREATE_ENABLED


def find_group_by_email(email):
    # Case insensitive search by group rep email for approved groups
    group = Group.objects.filter(
        rep_email__iexact=email,
        status__exact='approved',
    ).first()
    return group


# Organizing Hub templates
@register.inclusion_tag('partials/group_link.html', takes_context=True)
def group_link(context):

    group = find_group_by_email(context['request'].user.email)

    return {
        'group': group,
        'request': context['request'],
    }


# Organizing Hub Navigation menu
@register.inclusion_tag('partials/group_portal_nav.html', takes_context=True)
def group_portal_nav(context):

    group = find_group_by_email(context['request'].user.email)

    return {
        'group': group,
        'organizing_guides_url': settings.ORGANIZING_GUIDES_URL,
        'organizing_docs_url': settings.ORGANIZING_DOCS_URL,
        'request': context['request'],
    }
