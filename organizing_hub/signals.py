# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from calls.models import CallCampaign, CallCampaignStatus
from contacts.models import ContactList, ContactListStatus
from events.models import EventPromotion, EventPromotionStatus
from local_groups.models import (Group as LocalGroup, LocalGroupAffiliation)
from organizing_hub.tasks import (
    build_and_send_event_promotion,
    build_list_for_call_campaign,
)
from .views import (
    add_local_group_role_for_user,
    remove_local_group_role_for_user
)
import logging

logger = logging.getLogger(__name__)

LOCAL_GROUPS_ROLE_GROUP_LEADER_ID = settings.LOCAL_GROUPS_ROLE_GROUP_LEADER_ID


def sync_group_leader_affiliation_for_local_group(local_group):
    """
    Sync Group Leader Affiliation for Local Group
    """

    """Only sync for approved local group, otherwise do nothing"""
    if local_group.status == 'approved':

        """Find group leader user in db if it exists"""
        try:
            group_leader_user = User.objects.get(
                email__iexact=local_group.rep_email
            )
        except User.DoesNotExist:
            group_leader_user = None

        """Remove outdated group leader affiliations"""
        old_group_leader_affiliations = LocalGroupAffiliation.objects.filter(
            local_group=local_group,
            local_group_roles=LOCAL_GROUPS_ROLE_GROUP_LEADER_ID
        ).exclude(local_group_profile__user=group_leader_user)
        for old_group_leader_affiliation in old_group_leader_affiliations:
            remove_local_group_role_for_user(
                old_group_leader_affiliation.local_group_profile.user,
                local_group,
                LOCAL_GROUPS_ROLE_GROUP_LEADER_ID
            )

        """Add group leader role for user if it exists"""
        if group_leader_user:
            add_local_group_role_for_user(
                group_leader_user,
                local_group,
                LOCAL_GROUPS_ROLE_GROUP_LEADER_ID
            )


def sync_group_leader_affiliation_for_user(user):

    """Get list of Local Groups with user as rep email (group leader)"""
    local_groups_lead_by_user = LocalGroup.objects.filter(
        rep_email__iexact=user.email,
        status__exact='approved',
    )

    """Remove Group Leader role for non-matching Groups"""

    if hasattr(user, 'localgroupprofile'):
        local_group_profile = user.localgroupprofile

        """Get outdated Group Leader Affiliations for User"""
        group_leader_affiliations = local_group_profile.get_affiliations_for_local_group_role_id(
            LOCAL_GROUPS_ROLE_GROUP_LEADER_ID
        )
        old_affiliations = group_leader_affiliations.exclude(
            local_group__in=local_groups_lead_by_user
        )
        for old_affiliation in old_affiliations:
            remove_local_group_role_for_user(
                user,
                old_affiliation.local_group,
                LOCAL_GROUPS_ROLE_GROUP_LEADER_ID
            )

    """Add Group Leader role for matching Groups"""
    for local_group_lead_by_user in local_groups_lead_by_user:
        add_local_group_role_for_user(
            user,
            local_group_lead_by_user,
            LOCAL_GROUPS_ROLE_GROUP_LEADER_ID
        )


"""Signals"""


@receiver(post_save, sender=CallCampaign)
def call_campaign_post_save_handler(instance, **kwargs):
    """
    Call Campaign post-save handler

    Parameters
    ----------
    instance : CallCampaign
        Call Campaign
    """

    call_campaign = instance

    """Check if Call Campaign is New and Contact List is None"""
    status = call_campaign.status
    contact_list = call_campaign.contact_list
    if status == CallCampaignStatus.new.value[0] and contact_list is None:

        """Create New Contact List and add to Call Campaign"""
        list_name = 'List for Call Campaign: ' + str(call_campaign)
        contact_list = ContactList.objects.create(name=list_name)
        call_campaign.contact_list = contact_list
        call_campaign.save()

        """Call async task to build Contact List for Call Campaign"""
        build_list_for_call_campaign.delay(call_campaign.id)

    # """Clear the contact list if it requires clearing"""
    # if event_promotion.requires_list_clear and contact_list is not None:
    #     event_promotion.contact_list = None
    #     event_promotion.save()


@receiver(post_save, sender=EventPromotion)
def event_promotion_post_save_handler(instance, **kwargs):
    """
    Generate contact list if event promotion is approved and does not have a
    contact list yet
    """
    event_promotion = instance
    status = event_promotion.status
    contact_list = event_promotion.contact_list
    if status == EventPromotionStatus.approved.value[0] and contact_list is None:
        """Create new contact list and add to event promotion"""
        list_name = 'List for Event Promotion: ' + str(event_promotion)
        contact_list = ContactList.objects.create(name=list_name)
        event_promotion.contact_list = contact_list
        event_promotion.save()

        """Call async task to build and send event promotion"""
        build_and_send_event_promotion.delay(event_promotion.id)

    """Clear the contact list if it requires clearing"""
    if event_promotion.requires_list_clear and contact_list is not None:
        event_promotion.contact_list = None
        event_promotion.save()


@receiver(post_save, sender=LocalGroup)
def local_group_post_save_handler(instance, **kwargs):
    sync_group_leader_affiliation_for_local_group(instance)


@receiver(post_save, sender=User)
def user_post_save_handler(instance, **kwargs):
    sync_group_leader_affiliation_for_user(instance)
