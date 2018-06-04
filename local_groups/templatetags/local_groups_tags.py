from django import template
from django.conf import settings
from local_groups.models import LocalGroupAffiliation

register = template.Library()


@register.simple_tag
def bsd_create_account_url():
    return settings.BSD_CREATE_ACCOUNT_URL


def find_local_group_for_user(user):
    """Get Local Group for User"""

    if hasattr(user, 'localgroupprofile'):
        local_group_profile = user.localgroupprofile
        local_group_affiliation = LocalGroupAffiliation.objects.filter(
            local_group_profile=local_group_profile,
            local_group__status__exact='approved',
        ).first()
        if local_group_affiliation:
            return local_group_affiliation.local_group

    return None


# Organizing Hub templates
@register.inclusion_tag('partials/group_link.html', takes_context=True)
def group_link(context):

    group = find_local_group_for_user(context['request'].user)

    return {
        'group': group,
        'request': context['request'],
    }


# Organizing Hub Navigation menu
@register.inclusion_tag('partials/group_portal_nav.html', takes_context=True)
def group_portal_nav(context):

    group = find_local_group_for_user(context['request'].user)

    return {
        'group': group,
        'organizing_guides_url': settings.ORGANIZING_GUIDES_URL,
        'organizing_docs_url': settings.ORGANIZING_DOCS_URL,
        'request': context['request'],
    }


@register.simple_tag
def organizing_email():
    return settings.ORGANIZING_EMAIL
