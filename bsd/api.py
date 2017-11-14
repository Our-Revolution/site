# -*- coding: utf-8 -*-
import os
from bsdapi.BsdApi import Factory as BsdApiFactory

BSD_API_HOST = os.environ['BSD_API_HOST']
BSD_API_ID = os.environ['BSD_API_ID']
BSD_API_SECRET = os.environ['BSD_API_SECRET']

class Bsd:
    api = BsdApiFactory().create(
        id = BSD_API_ID,
        secret = BSD_API_SECRET,
        host = BSD_API_HOST,
        port = 80,
        securePort = 443
    )
