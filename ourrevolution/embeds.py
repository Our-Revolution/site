from wagtail.wagtailembeds.oembed_providers import OEMBED_ENDPOINTS

import json
import re

from django.utils.six.moves.urllib import request as urllib_request
from django.utils.six.moves.urllib.error import URLError
from django.utils.six.moves.urllib.parse import urlencode
from django.utils.six.moves.urllib.request import Request

from wagtail.wagtailembeds.exceptions import EmbedNotFoundException
from wagtail.wagtailembeds.oembed_providers import get_oembed_provider


MONKEYPATCHED_OEMBED_ENDPOINTS = dict(OEMBED_ENDPOINTS, **{
        'https://www.facebook.com/plugins/video/oembed.{format}': [
            'https://www.facebook.com/[\\w\-]+/videos/\\d+/'
        ]
    })


def compile_endpoints():
    endpoints = {}
    for endpoint in MONKEYPATCHED_OEMBED_ENDPOINTS.keys():
        endpoint_key = endpoint.replace('{format}', 'json')

        endpoints[endpoint_key] = []
        for pattern in MONKEYPATCHED_OEMBED_ENDPOINTS[endpoint]:
            endpoints[endpoint_key].append(re.compile(pattern))

    return endpoints

OEMBED_ENDPOINTS_COMPILED = compile_endpoints()


def get_oembed_provider(url):
    for endpoint in OEMBED_ENDPOINTS_COMPILED.keys():
        for pattern in OEMBED_ENDPOINTS_COMPILED[endpoint]:
            if re.match(pattern, url):
                return endpoint

    return


def oembed_monkeypatched(url, max_width=None):
    # Find provider
    provider = get_oembed_provider(url)
    if provider is None:
        raise EmbedNotFoundException

    # Work out params
    params = {'url': url, 'format': 'json'}
    if max_width:
        params['maxwidth'] = max_width

    # Perform request
    request = Request(provider + '?' + urlencode(params))
    request.add_header('User-agent', 'Mozilla/5.0')
    try:
        r = urllib_request.urlopen(request)
    except URLError:
        raise EmbedNotFoundException
    oembed = json.loads(r.read().decode('utf-8'))

    # Convert photos into HTML
    if oembed['type'] == 'photo':
        html = '<img src="%s" />' % (oembed['url'], )
    else:
        html = oembed.get('html')

    # Return embed as a dict
    return {
        'title': oembed['title'] if 'title' in oembed else '',
        'author_name': oembed['author_name'] if 'author_name' in oembed else '',
        'provider_name': oembed['provider_name'] if 'provider_name' in oembed else '',
        'type': oembed['type'],
        'thumbnail_url': oembed.get('thumbnail_url'),
        'width': oembed.get('width'),
        'height': oembed.get('height'),
        'html': html,
    }