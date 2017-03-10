from __future__ import unicode_literals

from django.db import models
from localflavor.us.models import USStateField, USZipCodeField
from phonenumber_field.modelfields import PhoneNumberField
from multiselectfield import MultiSelectField
from endorsements.models import Issue
from django_countries.fields import CountryField
from recurrence.fields import RecurrenceField
from django.contrib.gis.db.models import PointField

class Group(models.Model):    
    name = models.CharField(max_length=64, null=True, blank=False, verbose_name="Group Name")
    slug = models.SlugField(null=True, blank=False, unique=True)
    signup_date = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    group_id = models.CharField(max_length=4,null=True, blank=False)
    
    rep_email = models.EmailField(null=True, blank=False, verbose_name="Contact Email")
    rep_first_name = models.CharField(max_length=64, null=True, blank=False, verbose_name="First Name")
    rep_last_name = models.CharField(max_length=64, null=True, blank=False, verbose_name="Last Name")
    rep_postal_code = models.CharField(max_length=12, null=True, blank=True, verbose_name="Postal Code")
    rep_phone = PhoneNumberField(null=True, blank=True, verbose_name="Phone Number")
    
    county = models.CharField(max_length=11, null=True, blank=True)
    city = models.CharField(max_length=64, null=True, blank=True)
    state = USStateField(max_length=2, null=True, blank=True)
    postal_code = models.CharField(max_length=12, null=True, blank=False, verbose_name="Postal Code")
    country = CountryField(null=True, blank=False, default="US")
    point = PointField(null=True, blank=True)
        
    size = models.CharField(max_length=21, null=True, blank=True, verbose_name="Group Size")
    
    last_meeting = models.DateTimeField(null=True, blank=True, verbose_name="Date of Last Meeting")
    recurring_meeting = RecurrenceField(null=True, blank=True, verbose_name="Recurring Meeting", help_text='test')
    
    meeting_address_line1 = models.CharField("Address Line 1", max_length = 45, null=True, blank=True)
    meeting_address_line2 = models.CharField("Address Line 2", max_length = 45, null=True, blank=True)
    meeting_postal_code = models.CharField("Postal Code", max_length = 12, null=True, blank=True)
    meeting_city = models.CharField(max_length = 64, null=True, blank=True, verbose_name="City")
    meeting_state_province = models.CharField("State/Province", max_length = 40, null=True, blank=True)
    meeting_country = CountryField(null=True, blank=True, verbose_name="Country", default='US')
    
    TYPES_OF_ORGANIZING_CHOICES = (
        ('direct-action', 'Direct Action'),
        ('electoral', 'Electoral Organizing'),
        ('legistlative', 'Advocating for Legislation or Ballot Measures'),
        ('community', 'Community Organizing'),
        ('other', 'Other')
    )
    types_of_organizing = MultiSelectField(null=True, blank=True, choices=TYPES_OF_ORGANIZING_CHOICES, verbose_name="Types of Organizing")
    other_types_of_organizing = models.TextField(null=True, blank=True, verbose_name="Other Types of Organizing")
    
    description = models.TextField(null=True, blank=False, max_length=250, verbose_name="Description (250 characters or less)")
    issues = models.ManyToManyField(Issue, blank=True)
    other_issues = models.TextField(null=True, blank=True, max_length=250, verbose_name="Other Issues")
    
    constituency = models.TextField(null=True, blank=True, max_length=250)
    
    facebook_url = models.URLField(null=True, blank=True, verbose_name="Facebook URL")
    twitter_url = models.URLField(null=True, blank=True, verbose_name="Twitter URL")
    website_url = models.URLField(null=True, blank=True, verbose_name="Website URL")
    instagram_url = models.URLField(null=True, blank=True, verbose_name="Instagram URL")
    other_social = models.TextField(null=True, blank=True, verbose_name="Other Social Media", max_length=250)
    
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
