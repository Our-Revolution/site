from __future__ import unicode_literals
from django.conf import settings
from django.contrib.auth.models import Group as AuthGroup, User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Group as LocalGroup, LocalGroupAffiliation
import logging

logger = logging.getLogger(__name__)

AUTH_GROUP_LOCAL_GROUP_LEADER_ID = settings.AUTH_GROUP_LOCAL_GROUP_LEADER_ID


def sync_group_leader_affiliation_for_local_group(local_group):
    """
    Sync Group Leader Affiliation for Local Group
    """

    """
    TODO:
    only sync if group is approved, otherwise do nothing

    get all existing group leader affiliations for groups

    if it doesnt match expected group leader, remove role
    if none match expected group leader, and user exists, then add role

    if none match expected group leader, and user doesnt exist, do nothing
    if one matches expected group leader, do nothing
    """

    """Find group leader user in db if it exists"""
    try:
        group_leader_user = User.objects.get(
            email__iexact=local_group.rep_email
        )
    except User.DoesNotExist:
        group_leader_user = None
    logger.debug('group_leader_user: ' + str(group_leader_user))

    local_group_affiliations = LocalGroupAffiliation.objects.filter(
        local_group=local_group
    )
    logger.debug('local_group_affiliations: ' + str(local_group_affiliations))

    for affiliation in local_group_affiliations.filter(
        auth_groups__id=AUTH_GROUP_LOCAL_GROUP_LEADER_ID
    ):
        logger.debug('affiliation: ' + str(affiliation))
        if affiliation.local_group_profile.user is not group_leader_user:
            logger.debug('rm affiliation: ' + str(affiliation))
            affiliation.auth_groups.remove(AUTH_GROUP_LOCAL_GROUP_LEADER_ID)


@receiver(post_save, sender=LocalGroup)
def local_group_post_save_handler(instance, **kwargs):
    sync_group_leader_affiliation_for_local_group(instance)
