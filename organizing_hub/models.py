# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.utils.decorators import method_decorator
from django.utils.encoding import python_2_unicode_compatible
from enum import Enum, unique
from pages.models import AlertLevels
from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.fields import (
    RichTextField as WagtailRichTextField,
    StreamField,
)
from wagtail.wagtailcore.models import Page
from wagtail.wagtailsnippets.models import register_snippet
from local_groups.models import Group as LocalGroup
import logging

logger = logging.getLogger(__name__)


@unique
class OrganizingHubFeature(Enum):
    calling_tool = (1, 'Calling Tool')


class OrganizingHubAccess(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    local_group = models.OneToOneField(LocalGroup)

    def __unicode__(self):
        return '%s [%s] Access [%s]' % (
            self.local_group.name,
            self.local_group.slug,
            str(self.id),
        )


class OrganizingHubFeatureAccess(models.Model):
    feature = models.IntegerField(
        choices=[x.value for x in OrganizingHubFeature],
    )
    organizing_hub_access = models.ForeignKey(OrganizingHubAccess)

    def __unicode__(self):
        return '%s | %s' % (
            str(self.organizing_hub_access),
            self.get_feature_display(),
        )

    class Meta:
        unique_together = ["feature", "organizing_hub_access"]


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


@register_snippet
@python_2_unicode_compatible  # provide equivalent __unicode__ and __str__ methods on Python 2
class OrganizingHubLoginAlert(models.Model):
    content = WagtailRichTextField()
    show = models.BooleanField(
        default=False,
        help_text='Show alert on organizing hub login page.'
    )

    alert_level = models.IntegerField(
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
