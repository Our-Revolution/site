# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from wagtail.contrib.wagtailfrontendcache.backends import HTTPBackend
import fastly
import requests
import urlparse
import logging

logger = logging.getLogger(__name__)


FASTLY_API_KEY = settings.FASTLY_API_KEY
FASTLY_SERVICE_ID = settings.FASTLY_SERVICE_ID

fastly_api = fastly.API()
fastly_api.authenticate_by_key(FASTLY_API_KEY)


class FastlyBackend(HTTPBackend):

    def __init__(self, params):
        self.api_key = params.pop('API_KEY')
        self.hosts = params.pop('HOSTS')

    def get_surrogate_key_for_url(self, url):

        """Get surrogate key from url. Get path without trailing slash."""
        surrogate_key = urlparse.urlparse(url).path

        """Strip trailing slash unless homepage"""
        if surrogate_key != "/":
            surrogate_key = surrogate_key.rstrip('/')

        return surrogate_key

    def purge(self, url):

        """Get surrogate key from url. Get path without trailing slash."""
        surrogate_key = self.get_surrogate_key_for_url(url)
        logger.debug('surrogate_key: %s' % surrogate_key)

        """Purge surrogate key"""
        fastly_api.purge_key(FASTLY_SERVICE_ID, surrogate_key)
