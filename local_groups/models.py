from __future__ import unicode_literals

from django.db import models
from localflavor.us.models import USStateField, USZipCodeField
from phonenumber_field.modelfields import PhoneNumberField
from multiselectfield import MultiSelectField
from endorsements.models import Issue
from django_countries.fields import CountryField
from recurrence.fields import RecurrenceField
from address.models import AddressField
from django.contrib.gis.db.models import PointField

class Group(models.Model):    
    name = models.CharField(max_length=64, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)
    signup_date = models.DateTimeField(null=True, blank=True)
    
    rep_email = models.EmailField(null=True, blank=True)
    rep_first_name = models.CharField(max_length=9, null=True, blank=True)
    rep_last_name = models.CharField(max_length=12, null=True, blank=True)
    rep_postal_code = models.CharField(max_length=12, null=True, blank=True)
    rep_phone = PhoneNumberField(null=True, blank=True)
    
    county = models.CharField(max_length=11, null=True, blank=True)
    city = models.CharField(max_length=64, null=True, blank=True)
    state = USStateField(max_length=2, null=True, blank=True)
    postal_code = models.CharField(max_length=12, null=True, blank=True)
    country = CountryField(null=True)
    point = PointField(null=True, blank=False)
        
    size = models.CharField(max_length=21, null=True, blank=True)
    
    last_meeting = models.DateTimeField(null=True, blank=True)
    recurring_meeting = RecurrenceField(null=True, blank=True)
    recurring_meeting_location = AddressField(null=True, blank=True)
    
    TYPES_OF_ORGANIZING_CHOICES = (
        ('direct-action', 'Direct Action'),
        ('electoral', 'Electoral Organizing'),
        ('legistlative', 'Advocating for Legislation or Ballot Measures'),
        ('community', 'Community Organizing'),
        ('other', 'Other')
    )
    types_of_organizing = MultiSelectField(null=True, blank=True, choices=TYPES_OF_ORGANIZING_CHOICES)
    other_types_of_organizing = models.TextField(null=True, blank=True)
    
    description = models.TextField(null=True, blank=True)
    issues = models.ManyToManyField(Issue)
    other_issues = models.TextField(null=True, blank=True)
    
    leadership_structure = models.TextField(null=True, blank=True)
    constituency = models.TextField(null=True, blank=True)
    leadership_positions = models.TextField(null=True, blank=True)
    
    facebook_url = models.URLField(null=True, blank=True)
    twitter_url = models.URLField(null=True, blank=True)
    website_url = models.URLField(null=True, blank=True)
    instagram_url = models.URLField(null=True, blank=True)
    meetup_url = models.URLField(null=True, blank=True)
    other_social = models.TextField(null=True, blank=True)
    
    STATUSES = (
       ('submitted', 'Submitted'),
       ('signed-mou', 'Signed MOU'),
       ('approved', 'Approved'),
       ('removed', 'Removed') # can flesh out later
   ) 
    status = models.CharField(max_length=16, choices=STATUSES, default='submitted')
    # source = models.CharField(max_length=17, null=True, blank=True)
    # subsource = models.FloatField(null=True, blank=True)
    # i_p__address = models.CharField(max_length=16, null=True, blank=True)
    # constituent__id = models.IntegerField(null=True, blank=True)
    # signup__id = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.name
