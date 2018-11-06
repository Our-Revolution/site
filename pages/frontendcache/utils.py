import requests
from django.conf import settings
from wagtail.contrib.wagtailfrontendcache.utils import get_backends

FASTLY_SERVICE_ID = settings.FASTLY_SERVICE_ID
FASTLY_API_KEY = settings.FASTLY_API_KEY

def purge_all_from_cache(backend_settings=None, backends=None):
    """Utility method to purge all fastly cache, based on 
    wagtail.contrib.wagtailfrontendcache """
    for backend_name in get_backends(backend_settings=backend_settings, backends=backends).items():

        """Call purge all if backend is Fastly"""
        if backend_name == 'fastly':
            purge_url = 'https://api.fastly.com/service/%s/purge_all' % FASTLY_SERVICE_ID

            req = requests.request(
                'POST',
                purge_url,
                headers={'Fastly-Key': FASTLY_API_KEY}
            )
            assert req.status_code == 200
