# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import urlparse

import requests
from django.conf import settings
from wagtail.contrib.wagtailfrontendcache.backends import HTTPBackend

import fastly

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

        """Get path from url"""
        path = urlparse.urlparse(url).path

        """Strip trailing slash unless homepage"""
        if path != "/":
            surrogate_key = path.rstrip('/')
        else:
            surrogate_key = path

        return surrogate_key

    def purge(self, url):

        """Get surrogate key for url"""
        surrogate_key = self.get_surrogate_key_for_url(url)

        """Purge surrogate key"""
        fastly_api.purge_key(FASTLY_SERVICE_ID, surrogate_key)

    def purge_all(self):
        logger.info("Purging All")
        fastly_api.purge_service(FASTLY_SERVICE_ID)
