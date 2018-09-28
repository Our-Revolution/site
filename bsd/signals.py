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

    """Update result for new GeoTarget with async task"""
    if geo_target.status == GeoTargetStatus.new.value[0]:
        update_geo_target_result.delay(geo_target.id)
