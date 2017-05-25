from __future__ import unicode_literals

from django.db import models
from localflavor.us.models import USStateField, USZipCodeField
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.

class Nomination(models.Model):
    group_name = models.CharField(max_length=64, null=True, blank=False, verbose_name="Group Name")
    group_id = models.CharField(max_length=4,null=True, blank=False, verbose_name="Group ID")
    group_nomination_process = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Group Nomination Process")   
    
    rep_email = models.EmailField(null=True, blank=False, verbose_name="Contact Email", max_length=254)
    rep_first_name = models.CharField(max_length=35, null=True, blank=False, verbose_name="First Name")
    rep_last_name = models.CharField(max_length=35, null=True, blank=False, verbose_name="Last Name")
    rep_phone = PhoneNumberField(null=True, blank=True, verbose_name="Phone Number")
    
    candidate_email = models.EmailField(null=True, blank=False, verbose_name="Candidate Email", max_length=255)
    candidate_first_name = models.CharField(max_length=255, null=True, blank=False, verbose_name="Candidate First Name")
    candidate_last_name = models.CharField(max_length=255, null=True, blank=False, verbose_name="Candidate Last Name")
    candidate_phone = PhoneNumberField(null=True, blank=True, verbose_name="Candidate Phone Number")
    candidate_office = models.CharField(null=True, max_length=255, blank=False, verbose_name="Candidate Office")
    candidate_state = USStateField(max_length=2, null=True, blank=True)
    candidate_website_url = models.URLField(null=True, blank=True, verbose_name="Candidate Website URL", max_length=255)
    candidate_facebook_url = models.URLField(null=True, blank=True, verbose_name="Candidate Facebook URL", max_length=255)
    candidate_twitter_url = models.URLField(null=True, blank=True, verbose_name="Candidate Twitter URL", max_length=255)
    candidate_instagram_url = models.URLField(null=True, blank=True, verbose_name="Candidate Instagram URL", max_length=255)
    candidate_youtube_url = models.URLField(null=True, blank=True, verbose_name="Candidate YouTube URL", max_length=255)
    
    candidate_progressive_champion = models.TextField(max_length=500, blank=False, null=True, verbose_name = "How is the candidate a progressive champion?")
    candidate_community = models.TextField(max_length=500, blank=False, null=True, verbose_name = "What has the candidate done for the community?")
    candidate_presidential_support = models.BooleanField(default=False, blank=False, verbose_name = "Did the candidate publicly support anyone in the Primaries or/and General Elections for President in 2016?")
    candidate_presidential_support_who = models.TextField(max_length=128, blank=True, null=True, verbose_name = "If yes, who?")
    candidate_platform = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Briefly describe the candidate's platform?")
    candidate_goals = models.TextField(max_length=500, blank=False, null=True, verbose_name = "What are some of the candidate's top goals?")
    candidate_plan = models.TextField(max_length=500, blank=False, null=True, verbose_name = "What does the candidate plan to accomplish while in office?")
    candidate_group_organizing = models.BooleanField(default=False, blank=False, verbose_name = "Are people in the nominating Our Revolution group willing to organize for the candidate?")
    candidate_group_organizing_actions = models.TextField(max_length=500, blank=False, null=True, verbose_name = "What actions will the group take and how many people have agreed to volunteer/work?")
    candidiate_importance_of_endorsement = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Why is an our Revolution national endorsement important in this race?")
