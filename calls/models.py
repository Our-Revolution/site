from __future__ import unicode_literals
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.db.models import PointField
from django.contrib.gis.geos import Point
from django.db import models
from django.utils import timezone
from enum import Enum, unique
from localflavor.us.models import USStateField
from contacts.models import Contact, ContactList
from local_groups.models import find_local_group_by_user, Group as LocalGroup
import datetime
import googlemaps
import logging
import uuid

logger = logging.getLogger(__name__)

CALLS_RECENT_CUTOFF_DAYS = settings.CALLS_RECENT_CUTOFF_DAYS
GOOGLE_MAPS_SERVER_KEY = settings.GOOGLE_MAPS_SERVER_KEY


@unique
class CallCampaignStatus(Enum):
    new = (1, 'New')
    approved = (10, 'Approved')
    in_progress = (20, 'In Progress')
    paused = (30, 'Paused')
    complete = (40, 'Complete')
    declined = (50, 'Declined')
    suspended = (60, 'Suspended')


"""Active Campaign Statuses - not in final/end state yet"""
call_campaign_statuses_active = [
    CallCampaignStatus.new,
    CallCampaignStatus.approved,
    CallCampaignStatus.in_progress,
    CallCampaignStatus.paused,
]

"""Statuses for Caller display"""
call_campaign_statuses_for_caller = [
    CallCampaignStatus.approved,
    CallCampaignStatus.in_progress,
    CallCampaignStatus.paused,
    CallCampaignStatus.complete,
]

"""
Statuses that require clearing the Contact List. If we want to retry then we
should generate new list.
"""
call_campaign_statuses_for_list_clear = [
    CallCampaignStatus.declined,
]

"""Statuses that should skip Contact List validation"""
call_campaign_statuses_skip_list_validation = [
    CallCampaignStatus.new,
    CallCampaignStatus.declined,
    CallCampaignStatus.suspended,
]

"""Campaign Statuses with data download available"""
call_campaign_statuses_with_data_download = [
    CallCampaignStatus.in_progress,
    CallCampaignStatus.paused,
    CallCampaignStatus.complete,
]


def find_active_call_by_campaign_and_caller(call_campaign, caller):
    """
    Find active Call for Call Campaign and Caller

    Parameters
    ----------
    call_campaign : CallCampaign
        Call Campaign for calls
    caller : CallProfile
        Call Profile for caller

    Returns
        -------
        Call
            Returns active Call, or None
    """
    calls = call_campaign.call_set.filter(caller=caller).all()

    """Find and return Call without a response"""
    for call in calls:
        if not call.has_response:
            return call

    """Otherwise return None"""
    return None


def find_calls_made_by_campaign(call_campaign):
    """
    Find all calls for this campaign that have a response

    Parameters
    ----------
    call_campaign : CallCampaign
        Call Campaign for calls

    Returns
        -------
        Call list
            Returns matching Call list for campaign
    """
    calls = call_campaign.call_set.all()
    calls_with_responses = [x for x in calls if x.has_response]
    return calls_with_responses


def find_calls_made_by_campaign_and_caller(call_campaign, call_profile):
    """
    Find calls made for this campaign by this caller

    Parameters
    ----------
    call_campaign : CallCampaign
        Call Campaign for calls
    call_profile : CallProfile
        Call Profile for caller

    Returns
        -------
        Call list
            Returns matching Call list for campaign and caller
    """
    calls_made = find_calls_made_by_campaign(call_campaign)
    calls_made_by_caller = [x for x in calls_made if x.caller == call_profile]
    return calls_made_by_caller


def find_campaigns_as_caller(call_profile):
    """
    Find public Call Campaigns that match Call Profile for Caller

    Only return campaigns with statuses that are meant for display to callers

    Parameters
    ----------
    call_profile : CallProfile
        CallProfile for caller

    Returns
        -------
        CallCampaign list
            Returns public matching CallCampaign list
    """
    campaigns_as_caller = call_profile.campaigns_as_caller.filter(
        status__in=[x.value[0] for x in call_campaign_statuses_for_caller],
    ).order_by('-date_created')
    return campaigns_as_caller


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

    """Check local group permissions and find matching campaigns"""
    user = call_profile.user
    if hasattr(user, 'localgroupprofile'):
        local_group_profile = user.localgroupprofile
        local_group = find_local_group_by_user(user)
        if local_group is not None:
            permission = 'calls.change_callcampaign'
            if local_group_profile.has_permission_for_local_group(
                local_group,
                permission
            ):
                return local_group.callcampaign_set.all().order_by(
                    '-date_created'
                )

    """Otherwise return empty list"""
    return CallCampaign.objects.none()


def find_contact_to_call_for_campaign(call_campaign):
    """
    Find Contact to call for Call Campaign


    Find a Contact that hasn't been called yet for this Campaign, or recently
    for another Campaign.

    Parameters
    ----------
    call_campaign : CallCampaign
        Call Campaign for Contact

    Returns
        -------
        Contact
            Return available Contact or None
    """

    recent_call_cutoff = get_recent_call_cutoff()
    for contact in call_campaign.contact_list.contacts.all():
        if Call.objects.filter(
            call_campaign=call_campaign,
            contact=contact,
        ).first() is None:

            """Check if Contact has received recent Call for any Campaign"""
            last_call_to_contact = find_last_call_to_contact(contact)
            if last_call_to_contact is not None and (
                last_call_to_contact.date_created > recent_call_cutoff
            ):
                """Remove from contact list"""
                call_campaign.contact_list.contacts.remove(contact)
            else:
                """Return Contact"""
                return contact

    """Otherwise return None"""
    return None


def find_last_call_by_external_id(contact_external_id):
    """
    Find most recent Call created for Contact based on external id

    Parameters
    ----------
    contact_external_id : str
        Contact external_id field

    Returns
        -------
        Call
            Returns matching Call, or None
    """

    """See if there is a matching contact"""
    contact = Contact.objects.filter(external_id=contact_external_id).first()
    if contact is None:
        return None

    return find_last_call_to_contact(contact)


def find_last_call_to_contact(contact):
    """
    Find most recent Call created for Contact

    Parameters
    ----------
    contact : Contact
        Contact to check for

    Returns
        -------
        Call
            Returns matching Call, or None
    """

    """Check if Contact is None"""
    if contact is None:
        return None

    """Find last Call created for Contact"""
    last_call_created = Call.objects.filter(contact=contact).order_by(
        '-date_created'
    ).first()

    return last_call_created


def find_or_create_active_call_for_campaign_and_caller(call_campaign, caller):
    """
    Find or Create active Call for Call Campaign and Caller

    Parameters
    ----------
    call_campaign : CallCampaign
        Call Campaign for calls
    caller : CallProfile
        Call Profile for caller

    Returns
        -------
        Call
            Returns existing or new active Call, or None
    """

    """Check if there is an existing active Call"""
    call_existing = find_active_call_by_campaign_and_caller(
        call_campaign,
        caller,
    )
    if call_existing is not None:
        return call_existing

    """Find a Contact that hasn't been called and create a new Call"""
    """TODO: handle race condition error. find new contact and retry."""
    contact = find_contact_to_call_for_campaign(call_campaign)

    if contact is None:
        return None

    call_new = Call.objects.create(
        call_campaign=call_campaign,
        contact=contact,
        caller=caller,
    )
    return call_new


def get_recent_call_cutoff():
    """
    Get recent Call cutoff datetime for excluding Contacts from Calls

    Returns
        -------
        datetime
            Return recent Call cutoff datetime
    """
    recent_call_cutoff = timezone.now() - datetime.timedelta(
        days=CALLS_RECENT_CUTOFF_DAYS
    )
    return recent_call_cutoff


def save_call_response(call, question, answer):
    CallResponse.objects.update_or_create(
        call=call,
        question=question,
        defaults={
            'call': call,
            'question': question,
            'answer': answer,
        },
    )


def set_point_for_call_campaign(call_campaign):
    """
    Set point field on Call Campaign based on campaign zip code but don't save

    Parameters
    ----------
    call_campaign : CallCampaign
        Call Campaign to update

    Returns
        -------
        call_campaign
            Updated Call Campaign
    """

    """Get lat/long for zip from google maps api"""
    try:
        geolocator = googlemaps.Client(key=GOOGLE_MAPS_SERVER_KEY)
        components = {"postal_code": call_campaign.postal_code}
        geocoded_address = geolocator.geocode(components=components)
        location = geocoded_address[0]['geometry']['location']
        call_campaign.point = Point(
            location['lng'],
            location['lat'],
            srid=4326
        )
    except IndexError:
        """Set point to None if can't find lat/long"""
        if call_campaign.point is not None:
            call_campaign.point = None

    return call_campaign


class CallProfile(models.Model):
    """Calls app related information for a user"""

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __unicode__(self):
        return self.user.email + " [" + str(self.user.id) + "]"


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
    postal_code = models.CharField(max_length=12, verbose_name="Zip Code")
    script = models.TextField(max_length=2000)
    state_or_territory = USStateField(verbose_name="State or Territory")
    status = models.IntegerField(
        choices=[x.value for x in CallCampaignStatus],
        default=CallCampaignStatus.new.value[0],
        help_text="""
        Contact List is required to be complete and non-empty for certain
        Campaign statuses.
        """,
    )
    title = models.CharField(max_length=128)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)

    def __unicode__(self):
        return '%s [%s]' % (self.title, self.id)

    def _calls_made_count(self):
        """Count how many calls have been made for this campaign"""
        calls_with_responses = find_calls_made_by_campaign(self)
        return len(calls_with_responses)
    calls_made_count = property(_calls_made_count)

    def _contacts_total_count(self):
        """Count how many total calls can be made for this campaign"""
        if self.contact_list:
            return self.contact_list.contacts.count()
        else:
            return 0
    contacts_total_count = property(_contacts_total_count)

    def _has_data_download(self):
        """Check if status is in list of statuses with data download"""
        return self.status in [
            x.value[0] for x in call_campaign_statuses_with_data_download
        ]
    has_data_download = property(_has_data_download)

    def _is_active(self):
        """Check if status is in list of active statuses"""
        return self.status in [
            x.value[0] for x in call_campaign_statuses_active
        ]
    is_active = property(_is_active)

    def _is_approved(self):
        """Check if status is approved"""
        return self.status == CallCampaignStatus.approved.value[0]
    is_approved = property(_is_approved)

    def _is_in_progress(self):
        """Check if status is in progress"""
        return self.status == CallCampaignStatus.in_progress.value[0]
    is_in_progress = property(_is_in_progress)

    def _is_paused(self):
        """Check if status is paused"""
        return self.status == CallCampaignStatus.paused.value[0]
    is_paused = property(_is_paused)

    def save(self, *args, **kw):
        """Update point if point is None or postal code field changed"""
        new = self
        if new.point is None:
            new = set_point_for_call_campaign(new)
        elif new.pk:
            old = CallCampaign.objects.get(pk=new.pk)
            if old.postal_code != new.postal_code:
                new = set_point_for_call_campaign(new)
        super(CallCampaign, new).save(*args, **kw)


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
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)

    def __unicode__(self):
        return 'Call [%s] | %s | %s' % (
            self.id,
            self.call_campaign,
            self.contact,
        )

    def _has_response(self):
        """Check if any Responses have been saved for this Call"""
        return self.callresponse_set.filter(answer__isnull=False).count() > 0
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
    talk_to_contact_why_not = (
        2,
        'If you did not talk to the contact, why not?',
        (
            CallAnswer.no_answer,
            CallAnswer.wrong_number,
            CallAnswer.busy,
            CallAnswer.not_home,
            CallAnswer.do_not_call,
        )
    )
    take_action = (3, 'Did the contact want to take action?', (
        CallAnswer.yes,
        CallAnswer.no,
    ))
    voice_message = (4, 'Did you leave a voice message?', (
        CallAnswer.yes,
        CallAnswer.no,
    ))
    text_message = (5, 'Did you send a text message?', (
        CallAnswer.yes,
        CallAnswer.no,
    ))
    opt_out = (6, 'Did the contact want to opt out?', (
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
    answer = models.IntegerField(
        blank=True,
        choices=[x.value for x in CallAnswer],
        null=True,
    )

    def __unicode__(self):
        return 'Response [%s] | %s' % (self.id, self.call)

    class Meta:
        unique_together = ["call", "question"]
