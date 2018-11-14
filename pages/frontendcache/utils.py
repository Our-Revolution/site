import logging

import requests
from django.conf import settings
from wagtail.contrib.wagtailfrontendcache.utils import get_backends

import fastly

logger = logging.getLogger(__name__)

FASTLY_SERVICE_ID = settings.FASTLY_SERVICE_ID
FASTLY_API_KEY = settings.FASTLY_API_KEY

fastly_api = fastly.API()
fastly_api.authenticate_by_key(FASTLY_API_KEY)


def purge_all_from_cache(backend_settings=None, backends=None):
    """Utility method to purge all fastly cache, based on 
    wagtail.contrib.wagtailfrontendcache.utils"""
    
    for backend_name in get_backends(backend_settings=backend_settings, backends=backends):
        """Call purge all if backend is Fastly"""
        if backend_name == 'fastly':
            logger.info("[%s] Purging All", backend_name)
            fastly_api.purge_service(FASTLY_SERVICE_ID)
