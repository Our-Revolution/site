# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from pages.frontendcache.utils import purge_all_from_cache
from pages.models import SplashModal

logger = logging.getLogger(__name__)


@receiver(post_save, sender=SplashModal)
def splash_modal_post_save_handler(instance, **kwargs):
    """Purge all when Splash Modal is saved"""
    purge_all_from_cache()
