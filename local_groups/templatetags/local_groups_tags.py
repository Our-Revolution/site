from django import template
from pages.models import Group

register = template.Library()


# Groups Portal Navigation menu
@register.inclusion_tag('partials/group_portal_nav.html', takes_context=True)
def group_portal_nav(context):

    group = Group.objects.filter(
        rep_email=context['request'].user.email
    ).first()

    return {
        'group': group,
        'request': context['request'],
    }
