# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from bsd.models import GeoTarget, GeoTargetStatus
from bsd.tasks import update_geo_target_result
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=GeoTarget)
def geo_target_post_save_handler(instance, **kwargs):
    """
    Update GeoTarget with result from BSD


    Parameters
    ----------
    instance : GeoTarget
        GeoTarget instance
    """

    geo_target = instance

    """Check if status is new"""
    if geo_target.status == GeoTargetStatus.new.value[0]:

        """Set to in progress and update result with async task"""
        geo_target.status = GeoTargetStatus.in_progress.value[0]
        geo_target.save()
        update_geo_target_result.delay(geo_target.id)
