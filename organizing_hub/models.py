# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import models
from django.utils.decorators import method_decorator
from django.utils.encoding import python_2_unicode_compatible
from enum import Enum, unique
from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.fields import (
    RichTextField as WagtailRichTextField,
    StreamField,
)
from wagtail.wagtailcore.models import Page
from wagtail.wagtailsnippets.models import register_snippet
import logging

logger = logging.getLogger(__name__)

class OrganizingHubDashboardPage(Page):
    body = StreamField([
        ('link_block', blocks.StructBlock([
            ('text', blocks.TextBlock()),
            ('url', blocks.URLBlock()),
        ])),
    ])

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]

    @method_decorator(login_required)
    def serve(self, request, *args, **kwargs):
        return super(OrganizingHubDashboardPage, self).serve(
            request,
            *args,
            **kwargs
        )

@unique
class AlertLevels(Enum):
    success = ('success', 'Success (Green)')
    info = ('info', 'Info (Blue)')
    warning = ('warning', 'Warning (Yellow)')
    danger = ('danger', 'Danger (Red)')

@register_snippet
@python_2_unicode_compatible  # provide equivalent __unicode__ and __str__ methods on Python 2
class OrganizingHubLoginAlert(models.Model):
    content = WagtailRichTextField()
    show = models.BooleanField(
        default=False,
        help_text='Show alert on organizing hub login page.'
    )

    alert_level = models.CharField(
        max_length=16,
        choices=[x.value for x in AlertLevels],
        default=AlertLevels.warning.value[0],
        blank=False,
        null=False,
        help_text="""
        Set the alert style corresponding to Bootstrap 3 alert levels.

        See: https://getbootstrap.com/docs/3.3/components/#alerts-dismissible
        """
    )

    panels = [
        FieldPanel('content'),
        FieldPanel('show'),
        FieldPanel('alert_level')
    ]

    def __str__(self):
        return self.content
