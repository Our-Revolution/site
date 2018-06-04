from __future__ import unicode_literals
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from local_groups.models import (Group as LocalGroup, LocalGroupAffiliation)
from .views import add_local_group_role_for_user
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
            old_group_leader_affiliation.local_group_roles.remove(
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
            old_affiliation.local_group_roles.remove(
                LOCAL_GROUPS_ROLE_GROUP_LEADER_ID
            )

    """Add Group Leader role for matching Groups"""
    for local_group_lead_by_user in local_groups_lead_by_user:
        add_local_group_role_for_user(
            user,
            local_group_lead_by_user,
            LOCAL_GROUPS_ROLE_GROUP_LEADER_ID
        )


@receiver(post_save, sender=LocalGroup)
def local_group_post_save_handler(instance, **kwargs):
    sync_group_leader_affiliation_for_local_group(instance)


@receiver(post_save, sender=User)
def user_post_save_handler(instance, **kwargs):
    sync_group_leader_affiliation_for_user(instance)
