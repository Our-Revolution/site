# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.apps import AppConfig


class BsdConfig(AppConfig):
    name = 'bsd'

    def ready(self):
        import signals
