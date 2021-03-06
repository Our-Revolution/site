# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from bsdapi.BsdApi import Factory as BsdApiFactory
from django.conf import settings


class BSD:
    api = BsdApiFactory().create(
        id=settings.BSD_API_ID,
        secret=settings.BSD_API_SECRET,
        host=settings.BSD_API_HOST,
        port=80,
        securePort=443
    )
