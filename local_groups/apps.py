from __future__ import unicode_literals

from django.apps import AppConfig


class LocalGroupsConfig(AppConfig):
    name = 'local_groups'

    def ready(self):
        import local_groups.signals
