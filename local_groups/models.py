from __future__ import unicode_literals

from django.db import models
from localflavor.us.models import USStateField
from phonenumber_field.modelfields import PhoneNumberField
from multiselectfield import MultiSelectField
from endorsements.models import Issue
from django_countries.fields import CountryField
from recurrence.fields import RecurrenceField
from django.contrib.gis.db.models import PointField
from wagtail.contrib.wagtailfrontendcache.utils import purge_url_from_cache


class Group(models.Model):
    name = models.CharField(
        max_length=64,
        null=True, blank=False,
        verbose_name="Group Name"
    )
    slug = models.SlugField(
        null=True, blank=False,
        unique=True,
        max_length=100
    )
    signup_date = models.DateTimeField(
        null=True,
        blank=True,
        auto_now_add=True
    )
    group_id = models.CharField(
        max_length=4,
        null=True,
        blank=False,
        unique=True
    )

    # Order by group priority
    GROUP_TYPES = (
        (1, 'State Organizing Committee'),
        (2, 'State Chapter'),
        (3, 'Campus'),
        (4, 'Local Group')
    )
    group_type = models.IntegerField(
        blank=False,
        null=False,
        choices=GROUP_TYPES,
        default=4
    )

    # Individual Rep Email should match BSD authentication account
    rep_email = models.EmailField(
        null=True,
        blank=False,
        verbose_name="Contact Email",
        max_length=254
    )
    # Public group email does not need to match BSD authentication account
    group_contact_email = models.EmailField(
        blank=True,
        help_text="""Optional Group Contact Email to publicly display an email
        different from Group Leader Email""",
        max_length=254,
        null=True,
    )
    rep_first_name = models.CharField(
        max_length=35,
        null=True,
        blank=False,
        verbose_name="First Name"
    )
    rep_last_name = models.CharField(
        max_length=35,
        null=True,
        blank=False,
        verbose_name="Last Name"
    )
    rep_postal_code = models.CharField(
        max_length=12,
        null=True,
        blank=True,
        verbose_name="Postal Code"
    )
    rep_phone = PhoneNumberField(
        null=True,
        blank=True,
        verbose_name="Phone Number"
    )

    county = models.CharField(max_length=64, null=True, blank=True)
    city = models.CharField(max_length=64, null=True, blank=True)
    state = USStateField(max_length=2, null=True, blank=True)
    postal_code = models.CharField(
        max_length=12,
        null=True,
        blank=True,
        verbose_name="Postal Code"
    )
    country = CountryField(null=True, blank=False, default="US")
    point = PointField(null=True, blank=True)

    size = models.CharField(
        max_length=21,
        null=True,
        blank=True,
        verbose_name="Group Size"
    )

    last_meeting = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date of Last Meeting"
    )
    recurring_meeting = RecurrenceField(
        null=True,
        blank=True,
        verbose_name="Recurring Meeting"
    )

    meeting_address_line1 = models.CharField(
        "Address Line 1",
        max_length=45,
        null=True,
        blank=True)
    meeting_address_line2 = models.CharField(
        "Address Line 2",
        max_length=45,
        null=True,
        blank=True
    )
    meeting_postal_code = models.CharField(
        "Postal Code",
        max_length=12,
        null=True,
        blank=True
    )
    meeting_city = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name="City"
    )
    meeting_state_province = models.CharField(
        "State/Province",
        max_length=40,
        null=True,
        blank=True
    )
    meeting_country = CountryField(
        null=True,
        blank=True,
        verbose_name="Country",
        default='US'
    )

    TYPES_OF_ORGANIZING_CHOICES = (
        ('direct-action', 'Direct Action'),
        ('electoral', 'Electoral Organizing'),
        ('legistlative', 'Advocating for Legislation or Ballot Measures'),
        ('community', 'Community Organizing'),
        ('other', 'Other')
    )
    types_of_organizing = MultiSelectField(
        null=True,
        blank=True,
        choices=TYPES_OF_ORGANIZING_CHOICES,
        verbose_name="Types of Organizing"
    )
    other_types_of_organizing = models.TextField(
        null=True,
        blank=True,
        verbose_name="Other Types of Organizing",
        max_length=500
    )

    description = models.TextField(
        null=True,
        blank=False,
        max_length=1000,
        verbose_name="Description (1000 characters or less)"
    )
    issues = models.ManyToManyField(Issue, blank=True)
    other_issues = models.TextField(
        null=True,
        blank=True,
        max_length=250,
        verbose_name="Other Issues")

    constituency = models.TextField(null=True, blank=True, max_length=250)

    facebook_url = models.URLField(
        null=True,
        blank=True,
        verbose_name="Facebook URL",
        max_length=255
    )
    twitter_url = models.URLField(
        null=True,
        blank=True,
        verbose_name="Twitter URL",
        max_length=255)
    website_url = models.URLField(
        null=True,
        blank=True,
        verbose_name="Website URL",
        max_length=255
    )
    instagram_url = models.URLField(
        null=True,
        blank=True,
        verbose_name="Instagram URL",
        max_length=255
    )
    other_social = models.TextField(
        null=True,
        blank=True,
        verbose_name="Other Social Media",
        max_length=250
    )

    STATUSES = (
        ('submitted', 'Submitted'),
        ('signed-mou', 'Signed MOU'),
        ('inactive', 'Inactive'),
        ('approved', 'Approved'),
        ('removed', 'Removed')
    )
    status = models.CharField(
        max_length=64,
        choices=STATUSES,
        default='submitted'
    )

    VERSIONS = (
        ('none', 'N/A'),
        ('1.0', 'Old'),
        ('1.1', 'Current'),
    )

    signed_mou_version = models.CharField(
        max_length=64,
        choices=VERSIONS,
        default='none',
        verbose_name='MOU Version',
        null=True,
        blank=True
    )

    ORGANIZERS = (
        ('juliana', 'Juliana'),
        ('basi', 'Basi'),
        ('kyle', 'Kyle'),
    )

    organizer = models.CharField(
        max_length=64,
        choices=ORGANIZERS,
        default=None,
        verbose_name='Organizer',
        null=True,
        blank=True
    )

    mou_url = models.URLField(
        null=True,
        blank=True,
        verbose_name="MOU URL",
        max_length=255
    )

    # Notes field for internal OR staff use
    notes = models.TextField(
        blank=True,
        help_text="""Please include dates here along with notes to make
                    reporting easier.""",
        null=True,
        verbose_name="Notes"
    )

    def save(self, *args, **kwargs):
        # TODO: make main groups url an environment variable
        # and replace hardcoded /groups throughout site

        super(Group, self).save(*args, **kwargs)

        if self.slug:
            purge_url_from_cache('/groups/')
            purge_url_from_cache('/groups/' + self.slug +'/')

    def __unicode__(self):
        return self.name


class Event(models.Model):
    TIME_ZONE_CHOICES = (('US/%s' % pair, pair) for pair in (
        'Eastern',
        'Central',
        'Mountain',
        'Pacific',
        'Alaska',
        'Hawaii'
    ))

    capacity = models.IntegerField(
        default=0,
        help_text="Including guests. Leave 0 for unlimited.",
        verbose_name='Capacity Limit',
    )
    contact_phone = models.CharField(max_length=25)
    creator_name = models.CharField(max_length=255, verbose_name='Host Name')
    name = models.CharField(max_length=128)
    description = models.TextField()
    duration = models.IntegerField()
    host_receive_rsvp_emails = models.IntegerField(
        default=1,
        verbose_name='Notify me when new people RSVP'
    )
    public_phone = models.IntegerField(
        default=1,
        verbose_name='Make my phone number public to attendees'
    )
    start_day = models.DateField(verbose_name='Date')
    start_time = models.TimeField(verbose_name='Start Time')
    start_tz = models.CharField(
        max_length=40,
        blank=False,
        null=True,
        verbose_name='Time Zone',
        choices=TIME_ZONE_CHOICES,
        default='America/Eastern'
    )
    venue_name = models.CharField(max_length=255, verbose_name='Venue Name')
    venue_addr1 = models.CharField(
        max_length=255,
        verbose_name='Venue Address'
    )
    venue_addr2 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Venue Address #2'
    )
    venue_city = models.CharField(max_length=64, verbose_name='Venue City')
    venue_country = models.CharField(
        max_length=2,
        verbose_name='Venue Country',
        default='US'
    )
    venue_directions = models.TextField(
        blank=True,
        null=True,
        verbose_name='Directions to Venue'
    )
    venue_state_cd = USStateField(verbose_name='Venue State')
    venue_zip = models.CharField(max_length=16, verbose_name='Venue Zip Code')

    class Meta:
        managed = False
