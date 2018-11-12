import logging
import urlparse

from django.conf import settings

import requests
from wagtail.contrib.wagtailfrontendcache.backends import HTTPBackend

logger = logging.getLogger(__name__)

FASTLY_API_KEY = settings.FASTLY_API_KEY
FASTLY_HOSTS = settings.FASTLY_HOSTS


class FastlyBackend(HTTPBackend):

    def __init__(self, params):
        """Required by Wagtail"""
        self.hosts = FASTLY_HOSTS

    def purge(self, url):
        """Purge a single URL with Fastly"""
        """TODO: TECH-1522 Implement Fastly Python Library"""
        for host in FASTLY_HOSTS:
            req = requests.request(
                'PURGE',
                urlparse.urljoin(host, urlparse.urlparse(url).path),
                headers={'Fastly-Key': FASTLY_API_KEY}
            )
            assert req.status_code == 200
