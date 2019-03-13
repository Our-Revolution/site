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
from calls.models import call_campaign_statuses_for_caller, CallCampaign
from local_groups.models import find_local_group_by_user, Group as LocalGroup
import logging

logger = logging.getLogger(__name__)


def find_campaigns_as_admin(call_profile):
    """
    Find Call Campaigns that match Local Group edit access for Call Profile

    Return campaigns where profile has edit access via local group

    Parameters
    ----------
    call_profile : CallProfile
        CallProfile for local group affiliation

    Returns
        -------
        CallCampaign list
            Returns matching CallCampaign list
    """

    """Check Feature Access and Local Group Permissions"""
    user = call_profile.user
    local_group = find_local_group_by_user(user)
    if local_group is not None and has_call_permission_for_local_group(
        user,
        local_group,
        'calls.change_callcampaign'
    ):
        return local_group.callcampaign_set.all().order_by(
            '-date_created'
        )

    """Otherwise return empty list"""
    return CallCampaign.objects.none()


def find_campaigns_as_caller(caller):
    """
    Find public Call Campaigns that match Call Profile for Caller

    Only return Campaigns with statuses that are meant for display to Callers.
    Also check if Campaign Local Group has Call Tool Feature Access.

    Parameters
    ----------
    caller : CallProfile
        CallProfile for caller

    Returns
        -------
        CallCampaign list
            Returns public matching CallCampaign list
    """

    """Get Campaigns for Caller"""
    campaigns_as_caller = caller.campaigns_as_caller.filter(
        status__in=[x.value[0] for x in call_campaign_statuses_for_caller],
    ).order_by('-date_created')

    """Check Call Tool Feature Access for Campaigns"""
    campaigns = [x for x in campaigns_as_caller if has_call_feature_access_for_local_group(
        x.local_group
    )]

    return campaigns


def has_call_feature_access_for_local_group(local_group):
    """
    Check if Local Group has Call Tool Feature Access

    Parameters
    ----------
    local_group : LocalGroup
        Local Group to check for access

    Returns
        -------
        bool
            Return True if Local Group has Call Feature Access
    """

    """Check Feature Access"""
    if hasattr(local_group, 'organizinghubaccess'):
        access = local_group.organizinghubaccess
        return access.has_feature_access(OrganizingHubFeature.call_tool)

    """Otherwise False"""
    return False


def has_call_permission_for_local_group(user, local_group, permission):
    """
    Check if User has Call Tool Feature and Permission Access for Local Group

    Parameters
    ----------
    user : User
        User to check for access
    local_group : LocalGroup
        Local Group to check for access
    permission : str
        Permission code to check for access

    Returns
        -------
        bool
            Return True if User has Call Feature and Permission Access
    """

    """Check Feature Access and Local Group Permissions"""
    if hasattr(user, 'localgroupprofile'):
        local_group_profile = user.localgroupprofile
        if has_call_feature_access_for_local_group(local_group):
            return local_group_profile.has_permission_for_local_group(
                local_group,
                permission
            )

    """Otherwise False"""
    return False


def is_caller_for_call_campaign(call_profile):
    """
    Check if Call Profile is a Caller for any public Call Campaigns

    Only count campaigns with statuses that are meant for display to callers

    Parameters
    ----------
    call_profile : CallProfile
        CallProfile for caller

    Returns
        -------
        bool
            Return True if any matches exist
    """
    caller_campaigns = find_campaigns_as_caller(call_profile)
    is_caller = len(caller_campaigns) > 0
    return is_caller


@unique
class OrganizingHubFeature(Enum):
    call_tool = (1, 'Call Tool')
    nominations_priority_support = (2, 'Nominations: Priority Support')


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
            unicode(self.organizing_hub_access),
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
        context['call_tool_feature_id'] = OrganizingHubFeature.call_tool.value[0]

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
