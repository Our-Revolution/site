# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
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
from calls.models import is_caller_for_call_campaign
from local_groups.models import Group as LocalGroup
import logging

logger = logging.getLogger(__name__)


@unique
class OrganizingHubFeature(Enum):
    call_tool = (1, 'Call Tool')


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

    def has_feature_access(self, feature):
        """
        Check if a specific Feature is enabled for Access

        Parameters
        ----------
        feature : OrganizingHubFeature
            Organizing Hub Feature

        Returns
            -------
            bool
                Returns True if Feature is enabled for Access
        """

        return self.has_feature_access_by_id(feature.value[0])

    def has_feature_access_by_id(self, feature_id):
        """
        Check if a specific Feature id is enabled for Access

        Parameters
        ----------
        feature_id : int
            Organizing Hub Feature id

        Returns
            -------
            bool
                Returns True if Feature is enabled for Access
        """

        return self.organizinghubfeatureaccess_set.filter(
            feature=feature_id
        ).first() is not None


class OrganizingHubFeatureAccess(models.Model):
    feature = models.IntegerField(
        choices=[x.value for x in OrganizingHubFeature],
    )
    organizing_hub_access = models.ForeignKey(OrganizingHubAccess)

    def __unicode__(self):
        return '%s | %s' % (
            self.get_feature_display(),
            str(self.organizing_hub_access),
        )

    class Meta:
        unique_together = ["feature", "organizing_hub_access"]


class OrganizingHubDashboardPage(Page):
    body = StreamField([
        ('link_block', blocks.StructBlock([
            ('text', blocks.TextBlock()),
            ('url', blocks.URLBlock()),
            ('feature_access_required', blocks.ChoiceBlock(
                choices=[x.value for x in OrganizingHubFeature],
                help_text='''
                Select Feature if access should be restricted only to local
                groups that have this Feature enabled.
                ''',
                required=False,
            )),
        ])),
    ])

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]

    def get_context(self, request):
        context = super(OrganizingHubDashboardPage, self).get_context(request)

        """Check if User is a Caller for Call Tool and add to context"""
        user = request.user
        if hasattr(user, 'callprofile'):
            is_caller = is_caller_for_call_campaign(user.callprofile)
        else:
            is_caller = False
        context['is_caller'] = is_caller

        """Add Call Tool Feature id to context"""
        context['call_tool_feature_id'] = OrganizingHubFeature.calling_tool.value[0]

        return context

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
