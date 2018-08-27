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

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
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
    contact_list = models.OneToOneField(
        ContactList,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
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

    def _calls_made(self):
        """Count how many calls have been made for this campaign"""
        calls = self.call_set.all()
        calls_with_responses = [x for x in calls if x.has_response]
        return len(calls_with_responses)
    calls_made = property(_calls_made)

    def _calls_total(self):
        """Count how many total calls can be made for this campaign"""
        if self.contact_list:
            return self.contact_list.contacts.count()
        else:
            return None
    calls_total = property(_calls_total)


class Call(models.Model):
    """
    Call Model

    This represents a potential call or text being made to a contact
    """
    call_campaign = models.ForeignKey(CallCampaign)
    caller = models.ForeignKey(CallProfile)
    contact = models.ForeignKey(Contact)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return 'Call [%s] | %s' % (self.id, self.call_campaign)

    def _has_response(self):
        """Check if any Responses have been saved for this Call"""
        return self.callresponse_set.count() > 0
    has_response = property(_has_response)

    class Meta:
        unique_together = ["call_campaign", "contact"]


@unique
class CallAnswer(Enum):
    yes = (1, 'Yes')
    no = (2, 'No')
    maybe = (3, 'Maybe')
    no_answer = (4, 'No answer')
    wrong_number = (5, 'Wrong number')
    busy = (6, 'Busy')
    not_home = (7, 'Not Home')
    do_not_call = (8, 'Do not call')


@unique
class CallQuestion(Enum):
    talk_to_contact = (1, 'Did you talk to the contact?', (
        CallAnswer.yes,
        CallAnswer.no,
    ))
    talk_to_contact_why_not = (2, 'Why not?', (
        CallAnswer.no_answer,
        CallAnswer.wrong_number,
        CallAnswer.busy,
        CallAnswer.not_home,
        CallAnswer.do_not_call,
    ))
    take_action = (3, 'Does the contact want to take action with your group?', (
        CallAnswer.yes,
        CallAnswer.no,
    ))
    voice_message = (4, 'Did you leave a voicemail?', (
        CallAnswer.yes,
        CallAnswer.no,
    ))
    text_message = (5, 'Did you send a text message?', (
        CallAnswer.yes,
        CallAnswer.no,
    ))


class CallResponse(models.Model):
    """
    Call Response Model

    This represents a response to a question during a Call
    """

    call = models.ForeignKey(Call)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    question = models.IntegerField(choices=[
        (x.value[0], x.value[1]) for x in CallQuestion
    ])
    answer = models.IntegerField(choices=[x.value for x in CallAnswer])

    def __unicode__(self):
        return 'Response [%s] | %s' % (self.id, self.call)

    class Meta:
        unique_together = ["call", "question"]
