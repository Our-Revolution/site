from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.contrib.gis.db.models import PointField
from django.db import models
from enum import Enum, unique
from contacts.models import Contact, ContactList
from local_groups.models import Group as LocalGroup
import logging

logger = logging.getLogger(__name__)


class CallProfile(models.Model):
    """Calls app related information for a user"""

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __unicode__(self):
        return self.user.email + " [" + str(self.user.id) + "]"


@unique
class CallCampaignStatus(Enum):
    new = (1, 'New')
    approved = (10, 'Approved')
    in_progress = (20, 'In Progress')
    paused = (30, 'Paused')
    complete = (40, 'Complete')
    declined = (50, 'Declined')
    suspended = (60, 'Suspended')


class CallCampaign(models.Model):
    """
    Call Campaign Model

    This represents a calling campaign with potentially many calls and callers
    """

    callers = models.ManyToManyField(
        CallProfile,
        blank=True,
        related_name='campaigns_as_caller'
    )
    contact_list = models.ForeignKey(
        ContactList,
        blank=True,
        null=True,
    )
    local_group = models.ForeignKey(LocalGroup)
    """Max distance in miles"""
    max_distance = models.IntegerField()
    max_recipients = models.IntegerField()
    """User who initiated the campaign"""
    owner = models.ForeignKey(CallProfile, related_name='campaigns_as_owner')
    point = PointField(blank=True, null=True)
    postal_code = models.CharField(max_length=12)
    script = models.TextField(max_length=2000)
    status = models.IntegerField(
        choices=[x.value for x in CallCampaignStatus],
        default=CallCampaignStatus.new
    )
    title = models.CharField(max_length=128)

    def __unicode__(self):
        return '%s [%s]' % (self.title, self.id)


class Call(models.Model):
    """
    Call Model

    This represents a potential call or text being made to a contact
    """
    call_campaign = models.ForeignKey(CallCampaign)
    caller = models.ForeignKey(CallProfile)
    contact = models.ForeignKey(Contact)
    date_created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return 'Call [%s] | %s' % (self.id, self.call_campaign)
