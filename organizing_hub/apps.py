from __future__ import unicode_literals
from django.apps import AppConfig


class OrganizingHubConfig(AppConfig):
    name = 'organizing_hub'

    def ready(self):
        import signals
