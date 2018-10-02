# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.db import models
from django.utils.decorators import method_decorator
from django.utils.encoding import python_2_unicode_compatible
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

# TODO: implement alert levels
@register_snippet
@python_2_unicode_compatible  # provide equivalent __unicode__ and __str__ methods on Python 2
class OrganizingHubLoginAlert(models.Model):
    content = WagtailRichTextField()
    show = models.BooleanField(
        default=False,
        help_text='Show alert on organizing hub login page.'
    )

    panels = [
        FieldPanel('content'),
        FieldPanel('show'),
    ]

    def __str__(self):
        return self.content
