# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import template
from django.conf import settings
from django.urls import reverse_lazy
from calls.models import CallCampaignStatus
from local_groups.models import find_local_group_by_user
from organizing_hub.models import OrganizingHubLoginAlert
import logging

logger = logging.getLogger(__name__)

register = template.Library()

BSD_CREATE_ACCOUNT_URL = settings.BSD_CREATE_ACCOUNT_URL
ORGANIZING_DOCS_URL = settings.ORGANIZING_DOCS_URL
ORGANIZING_EMAIL = settings.ORGANIZING_EMAIL
ORGANIZING_GUIDES_URL = settings.ORGANIZING_GUIDES_URL
ORGANIZING_HUB_ADMINS_ENABLED = settings.ORGANIZING_HUB_ADMINS_ENABLED
ORGANIZING_HUB_CALL_CALLERS_URL = settings.ORGANIZING_HUB_CALL_CALLERS_URL
ORGANIZING_HUB_CALL_MANAGE_URL = settings.ORGANIZING_HUB_CALL_MANAGE_URL
ORGANIZING_HUB_CALL_SCRIPT_URL = settings.ORGANIZING_HUB_CALL_SCRIPT_URL
ORGANIZING_HUB_DASHBOARD_URL = settings.ORGANIZING_HUB_DASHBOARD_URL
ORGANIZING_HUB_PROMOTE_ENABLED = settings.ORGANIZING_HUB_PROMOTE_ENABLED


@register.simple_tag
def bsd_create_account_url():
    return BSD_CREATE_ACCOUNT_URL


@register.simple_tag
def call_campaign_complete_url(call_campaign):
    """
    URL for Complete Call Campaign page

    Parameters
    ----------
    call_campaign : CallCampaign
        Call Campaign

    Returns
        -------
        str
            Return url for Complete Call Campaign page
    """
    return reverse_lazy(
        'organizing-hub-call-campaign-status',
        kwargs={
            'uuid': call_campaign.uuid,
            'status_id': CallCampaignStatus.complete.value[0],
        }
    )


@register.simple_tag
def call_campaign_pause_url(call_campaign):
    """
    URL for Pause Call Campaign page

    Parameters
    ----------
    call_campaign : CallCampaign
        Call Campaign

    Returns
        -------
        str
            Return url for Pause Call Campaign page
    """
    return reverse_lazy(
        'organizing-hub-call-campaign-status',
        kwargs={
            'uuid': call_campaign.uuid,
            'status_id': CallCampaignStatus.paused.value[0],
        }
    )


@register.simple_tag
def call_campaign_resume_url(call_campaign):
    """
    URL for Resume Call Campaign page

    Parameters
    ----------
    call_campaign : CallCampaign
        Call Campaign

    Returns
        -------
        str
            Return url for Resume Call Campaign page
    """
    return reverse_lazy(
        'organizing-hub-call-campaign-status',
        kwargs={
            'uuid': call_campaign.uuid,
            'status_id': CallCampaignStatus.in_progress.value[0],
        }
    )


@register.simple_tag
def call_campaign_start_url(call_campaign):
    """
    URL for Start Call Campaign page

    Parameters
    ----------
    call_campaign : CallCampaign
        Call Campaign

    Returns
        -------
        str
            Return url for Start Call Campaign page
    """
    return reverse_lazy(
        'organizing-hub-call-campaign-status',
        kwargs={
            'uuid': call_campaign.uuid,
            'status_id': CallCampaignStatus.in_progress.value[0],
        }
    )


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
def has_organizing_hub_feature_access(context, feature_id):
    """
    Check if user has access to Organizing Hub Feature

    Parameters
    ----------
    feature_id : int
        Organizing Hub Feature id

    Returns
        -------
        bool
            Return True if user has access to Organizing Hub Feature
    """
    local_group = find_local_group_by_user(context['request'].user)
    if local_group is not None and hasattr(
        local_group,
        'organizinghubaccess',
    ):
        access = local_group.organizinghubaccess
        has_feature_access = access.has_feature_access_by_id(feature_id)
        return has_feature_access
    else:
        return False


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
def organizing_docs_url():
    return ORGANIZING_DOCS_URL


@register.simple_tag
def organizing_email():
    return ORGANIZING_EMAIL


@register.simple_tag
def organizing_hub_call_callers_url():
    return ORGANIZING_HUB_CALL_CALLERS_URL


@register.simple_tag
def organizing_hub_call_manage_url():
    return ORGANIZING_HUB_CALL_MANAGE_URL


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
