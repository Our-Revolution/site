from __future__ import unicode_literals
from django.conf import settings
from django.db.models import Group as LocalGroup, LocalGroupAffiliation
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)


def sync_group_leader_affiliation_for_local_group(local_group):
    """
    Sync Group Leader Affiliatino for Local Group
    """

    # Find group leader user in db if it exists
    try:
        group_leader_user = User.objects.get(
            email__iexact=local_group.rep_email
        )

    except User.DoesNotExist:
        group_leader_user = None

    local_group_affiliations = LocalGroupAffiliation.objects.filter(
        local_group=local_group
    )

    """
    split affiliations into 2 category: matches group leader user, or not
    if matches group leader user, see if leader role is present, and add if not
    if none match group leader user, then
    if doesnt match group leader user, see if leader role is present, and remove if yes
    """
    for local_group_affiliation in local_group_affiliations:
        if local_group_affiliation.auth_groups.filter(
            id=settings.LOCAL_GROUPS_ROLE_GROUP_LEADER_ID
        ).exists()


@receiver(post_save, sender=LocalGroup)
def local_group_post_save_handler(instance, **kwargs):
    sync_group_leader_affiliation_for_local_group(instance)
