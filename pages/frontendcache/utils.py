import logging

import requests
from django.conf import settings
from wagtail.contrib.wagtailfrontendcache.utils import get_backends

import fastly

logger = logging.getLogger(__name__)


def purge_all_from_cache(backend_settings=None, backends=None):
    """Utility method to purge all from cache, based on 
    wagtail.contrib.wagtailfrontendcache.utils"""
    
    for backend_name, backend in get_backends(backend_settings=backend_settings, backends=backends).items():
        """Check that backend has purge_all implemented"""
        try:
            backend.purge_all()
            logger.info("[%s] Purging All", backend_name)
        except AttributeError:
            logger.error("[%s] Backend does not support purge_all.", backend_name)
