from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from wagtail.wagtailadmin.edit_handlers import StreamFieldPanel
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore.models import Page
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
            request,
            *args,
            **kwargs
        )
