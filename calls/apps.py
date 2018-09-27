from __future__ import unicode_literals
from django.apps import AppConfig


class CallsConfig(AppConfig):
    name = 'calls'

    def ready(self):
        import signals
