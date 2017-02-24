from __future__ import unicode_literals

from django.db import models
from localflavor.us.models import PhoneNumberField, USStateField, USZipCodeField


class Group(models.Model):
    name = models.CharField(max_length=64, null=True, blank=True)
    state = USStateField(max_length=2, null=True, blank=True)
    signup_date = models.DateTimeField(null=True, blank=True)
    rep_email = models.EmailField(null=True, blank=True)
    rep_first_name = models.CharField(max_length=9, null=True, blank=True)
    rep_last_name = models.CharField(max_length=12, null=True, blank=True)
    rep_zip_code = USZipCodeField(null=True, blank=True)
    rep_phone = models.IntegerField(null=True, blank=True)
    county = models.CharField(max_length=11, null=True, blank=True)
    city = models.CharField(max_length=64, null=True, blank=True)
    size = models.CharField(max_length=21, null=True, blank=True)
    last_meeting = models.DateTimeField(null=True, blank=True)
    types_of_organizing = models.TextField(null=True, blank=True)
    mission_vision = models.TextField(null=True, blank=True)
    issues = models.CharField(max_length=257, null=True, blank=True)
    leadership_structure = models.TextField(null=True, blank=True)
    constituency = models.TextField(null=True, blank=True)
    leadership_positions = models.TextField(null=True, blank=True)
    social_media = models.TextField(null=True, blank=True)
    # source = models.CharField(max_length=17, null=True, blank=True)
    # subsource = models.FloatField(null=True, blank=True)
    # i_p__address = models.CharField(max_length=16, null=True, blank=True)
    # constituent__id = models.IntegerField(null=True, blank=True)
    # signup__id = models.IntegerField(null=True, blank=True)