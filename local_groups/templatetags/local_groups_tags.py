from django import template
from django.conf import settings
from pages.models import Group

register = template.Library()


# Organizing Hub Navigation menu
@register.inclusion_tag('partials/group_portal_nav.html', takes_context=True)
def group_portal_nav(context):

    group = Group.objects.filter(
        rep_email__iexact=context['request'].user.email
    ).first()

    return {
        'group': group,
        'organizing_guides_url': settings.ORGANIZING_GUIDES_URL,
        'request': context['request'],
    }
