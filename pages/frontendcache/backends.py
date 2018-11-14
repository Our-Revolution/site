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

api = fastly.API()
api.authenticate_by_key(FASTLY_API_KEY)


class FastlyBackend(HTTPBackend):

    def __init__(self, params):
        self.api_key = params.pop('API_KEY')
        self.hosts = params.pop('HOSTS')

    def purge(self, url):
        """Get Surrogate Key"""
        skey = urlparse.urlparse(url).path.rstrip('/')
        logger.debug('skey: %s' % skey)

        for host in self.hosts:
            api.purge_key(FASTLY_SERVICE_ID, skey)

            # req = requests.request(
            #     'PURGE',
            #     urlparse.urljoin(host, urlparse.urlparse(url).path),
            #     headers={'Fastly-Key': self.api_key}
            # )
            # assert req.status_code == 200
