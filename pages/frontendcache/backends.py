from wagtail.contrib.wagtailfrontendcache.backends import HTTPBackend
import requests
import urlparse


class FastlyBackend(HTTPBackend):

    def __init__(self, params):
        self.api_key = params.pop('API_KEY')
        self.hosts = params.pop('HOSTS')

    def purge(self, url):
        for host in self.hosts:
            req = requests.request(
                'PURGE',
                urlparse.urljoin(host, urlparse.urlparse(url).path),
                headers={'Fastly-Key': self.api_key}
            )
            assert req.status_code == 200
