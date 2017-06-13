from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save
from localflavor.us.models import USStateField, USZipCodeField
from phonenumber_field.modelfields import PhoneNumberField
from local_groups.models import Group
    
#TODO: automate endorsement -> approval -> candidates page 
    
class Nomination(models.Model):
    group_nomination_process = models.TextField(max_length=500, blank=False, null=True, verbose_name = "Group Nomination Process") 
    
    # def __unicode__(self):
    #     if self.group_name 
    #     return str(self.group_name + ' - ' + self.candidate_first_name + ' ' + self.candidate_last_name)

    def __unicode__(self):
        return self.group.name

    def save(self, *args, **kwargs):
        super(Nomination, self).save(*args, **kwargs)
        if self.nominationresponse_set.count() == 0:
            for q in NominationQuestion.objects.all():
                self.nominationresponse_set.create(question=q)


class NominationQuestion(models.Model):
    text = models.TextField()

    def __unicode__(self):
        return self.text


class NominationResponse(models.Model):
    nomination = models.ForeignKey(Nomination)
    question = models.ForeignKey(NominationQuestion)
    response = models.TextField()

    def __unicode__(self):
        return unicode(self.question)


class Questionnaire(models.Model):
    """
    A platform questionnaire is filled out by the candidate with basic information and in-depth policy positions.
    """    
    
    #TODO: make sure we're getting all office/district/location info we need
     
    # Candidate Information and Social Media
    candidate_first_name = models.CharField(max_length=255, null=True, blank=False, verbose_name="Candidate First Name")
    candidate_last_name = models.CharField(max_length=255, null=True, blank=False, verbose_name="Candidate Last Name")
    candidate_email = models.EmailField(null=True, blank=False, verbose_name="Candidate Email", max_length=255)
    candidate_phone = PhoneNumberField(null=True, blank=True, verbose_name="Candidate Phone Number")
    candidate_office = models.CharField(null=True, max_length=255, blank=False, verbose_name="Candidate Office")
    candidate_district = models.CharField(null=True, max_length=255, blank=False, verbose_name="Candidate District")
    candidate_state = USStateField(max_length=2, null=True, blank=False, verbose_name="Candidate State")
    candidate_website_url = models.URLField(null=True, blank=True, verbose_name="Candidate Website URL", max_length=255)
    candidate_donate_url = models.URLField(null=True, blank=True, verbose_name="Candidate Donate URL", max_length=255)
    candidate_facebook_url = models.URLField(null=True, blank=True, verbose_name="Candidate Facebook URL", max_length=255)
    candidate_twitter_url = models.URLField(null=True, blank=True, verbose_name="Candidate Twitter URL", max_length=255)
    candidate_instagram_url = models.URLField(null=True, blank=True, verbose_name="Candidate Instagram URL", max_length=255)
    candidate_youtube_url = models.URLField(null=True, blank=True, verbose_name="Candidate YouTube URL", max_length=255)
    candidate_donate_url = models.URLField(null=True, blank=True, verbose_name="Candidate Donate URL", max_length=255)
    
    def __unicode__(self):
        return str(self.candidate_first_name + ' ' + self.candidate_last_name)

    def save(self, *args, **kwargs):
        super(Questionnaire, self).save(*args, **kwargs)
        if self.response_set.count() == 0:
            for q in Question.objects.all():
                self.response_set.create(question=q)


class Question(models.Model):
    text = models.TextField(verbose_name="Question Text")
    include_multi_choice = models.BooleanField(default=True, verbose_name="Include Multiple Choice Selection")

    def __unicode__(self):
        return self.text


class Response(models.Model):
    QUESTIONNAIRE_CHOICES = (
        ('a', 'Agree'),
        ('b', 'Disagree'),
        ('c', 'Mostly agree'),
        ('d', 'Mostly disagree'),
    )
    questionnaire = models.ForeignKey(Questionnaire)
    question = models.ForeignKey(Question)
    response = models.CharField(max_length=1, blank=True, null=True, choices=QUESTIONNAIRE_CHOICES)
    position = models.TextField(max_length=500, blank=False, null=True)

    def __unicode__(self):
        return unicode(self.question)



class Application(models.Model):
    """
    An application is a single submission for an endorsement. Each application consists of a group nomination and a candidate questionnaire, and has a many-to-one relationship with a group.
    """
    
    create_dt = models.DateTimeField(auto_now_add=True)
    
    nomination = models.OneToOneField(
        Nomination,
        on_delete=models.CASCADE,
        primary_key=False,
        null=True,
        blank=True
    )
    
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.SET_NULL, null=True, blank=True)
    
    group = models.ForeignKey(Group, to_field="group_id")
    
    rep_email = models.EmailField(null=True, blank=False, verbose_name="Contact Email", max_length=254)
    rep_first_name = models.CharField(max_length=35, null=True, blank=False, verbose_name="First Name")
    rep_last_name = models.CharField(max_length=35, null=True, blank=False, verbose_name="Last Name")
    rep_phone = PhoneNumberField(null=True, blank=True, verbose_name="Phone Number")
    
    #TODO: change to foreign key and create new object for each new candidate, implement autocomplete to  minimize duplicate candidates
    candidate_first_name = models.CharField(max_length=255, null=True, blank=False, verbose_name="Candidate First Name")
    candidate_last_name = models.CharField(max_length=255, null=True, blank=False, verbose_name="Candidate Last Name")
    candidate_office = models.CharField(null=True, max_length=255, blank=False, verbose_name="Candidate Office")
    candidate_district = models.CharField(null=True, max_length=255, blank=False, verbose_name="Candidate District")
    candidate_state = USStateField(max_length=2, null=True, blank=False)
    
    #TODO: Flesh out (get with E and G to figure out statuses)
    STATUSES = (
       ('incomplete', 'Incomplete'),
       ('submitted', 'Submitted'),
       ('approved', 'Approved'),
       ('removed', 'Denied')
   ) 
    status = models.CharField(max_length=16, choices=STATUSES, default='incomplete')
    
    def __unicode__(self):
        return str(self.group.name + ' - ' + self.candidate_first_name + ' ' + self.candidate_last_name)

    def save(self, *args, **kwargs):
        if not self.nomination:
            self.nomination = Nomination.objects.create()
        super(Application, self).save(*args, **kwargs)

