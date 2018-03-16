from __future__ import unicode_literals
from django.db import models
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page


class TransformPartyPage(Page):
    body = RichTextField()
    signup_embed_code = models.TextField(
        blank=True,
        null=True,
        help_text='Raw HTML embed code for signup form, etc.'
    )

    content_panels = Page.content_panels + [
        FieldPanel('signup_embed_code'),
        FieldPanel('body'),
    ]

    parent_page_types = ['transform.TransformPartyIndexPage']
    subpage_types = []


class TransformPartyIndexPage(Page):
    parent_page_types = ['pages.IndexPage']
    subpage_types = ['transform.TransformPartyPage']
