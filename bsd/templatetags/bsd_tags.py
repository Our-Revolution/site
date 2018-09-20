# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import template
from bsd.models import get_bsd_event_url

register = template.Library()


@register.simple_tag
def bsd_event_url(event_id_obfuscated):
    return get_bsd_event_url(event_id_obfuscated)
