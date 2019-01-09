from __future__ import unicode_literals
from ckeditor.fields import RichTextField
from collections import defaultdict
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from localflavor.us.models import USStateField
from local_groups.models import Group
from pages.models import AlertLevels
from phonenumber_field.modelfields import PhoneNumberField
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.fields import RichTextField as WagtailRichTextField
from wagtail.wagtailsnippets.models import register_snippet

import datetime
import logging

logger = logging.getLogger(__name__)


class Nomination(models.Model):
    """
    A nomination form is filled out by the group with basic information about
    the group and what it will do to help the candidate.
    """

    # TODO: move this into application model
    group_nomination_process = models.TextField(
        max_length=500,
        blank=False,
        null=True,
        verbose_name="Briefly describe your group's nomination process"
    )

    STATUSES = (
        ('incomplete', 'Incomplete'),
        ('complete', 'Complete'),
    )

    status = models.CharField(
        max_length=16,
        choices=STATUSES,
        default='incomplete',
        blank=True
    )

    def __unicode__(self):
        try:
            return self.application.candidate_first_name + ' ' + self.application.candidate_last_name + ' - ' + ' Nomination'
        except:
            return 'Nomination ' + str(self.pk)

    def save(self, *args, **kwargs):
        super(Nomination, self).save(*args, **kwargs)

        '''
        Save the application to update statuses and do other conditional logic
        if the nomination has an application, save that application
        '''
        if hasattr(self, 'application'):
            self.application.save()

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
    response = models.TextField(max_length=1000)

    def __unicode__(self):
        return unicode(self.question)


@register_snippet
@python_2_unicode_compatible  # provide equivalent __unicode__ and __str__ methods on Python 2
class NominationsPlatformAlert(models.Model):
    content = WagtailRichTextField()
    show = models.BooleanField(
        default=False,
        help_text='Show alert on nominations platform pages.'
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


class Questionnaire(models.Model):
    """
    A platform questionnaire is filled out by the candidate with basic information and in-depth policy positions.
    """

    STATUSES = (
        ('incomplete', 'Incomplete'),
        ('complete', 'Complete'),
        ('sent', 'Sent to Candidate'),
    )
    status = models.CharField(max_length=16, choices=STATUSES, default='incomplete', blank=True)

    # Candidate Information and Social Media
    candidate_first_name = models.CharField(max_length=255, null=True, blank=False, verbose_name="Candidate First Name")
    candidate_last_name = models.CharField(max_length=255, null=True, blank=False, verbose_name="Candidate Last Name")
    candidate_bio = models.TextField(max_length=1000, blank=False, null=False, verbose_name = "Candidate Bio")
    candidate_email = models.EmailField(null=True, blank=False, verbose_name="Candidate Email", max_length=255)
    candidate_phone = PhoneNumberField(null=True, blank=True, verbose_name="Candidate Phone Number")
    candidate_office = models.CharField(null=True, max_length=255, blank=False, verbose_name="Candidate Office")
    candidate_district = models.CharField(null=True, max_length=255, blank=True, verbose_name="Candidate District")
    candidate_party = models.CharField(null=True, max_length=255, blank=False, verbose_name="Candidate Party Affiliation")
    candidate_held_office = models.NullBooleanField(
        verbose_name="Has the candidate ever held public office?"
    )
    candidate_is_member = models.NullBooleanField(
        verbose_name="Is candidate a member of Our Revolution?"
    )
    candidate_city = models.CharField(null=True, max_length=255, blank=True, verbose_name="Candidate City")
    candidate_state = USStateField(max_length=2, null=True, blank=False, verbose_name="Candidate State")
    general_election_date = models.DateField(verbose_name = 'General Election Date', null = True, blank = False)
    primary_election_date = models.DateField(verbose_name = 'Primary Election Date', null = True, blank = True)
    candidate_website_url = models.URLField(null=True, blank=True, verbose_name="Candidate Website URL", max_length=255)
    candidate_volunteer_url = models.URLField(null=True, blank=True, verbose_name="Candidate Volunteer URL", max_length=255)
    candidate_donate_url = models.URLField(null=True, blank=True, verbose_name="Candidate Donate URL", max_length=255)
    candidate_facebook_url = models.URLField(null=True, blank=True, verbose_name="Candidate Facebook URL", max_length=255)
    candidate_twitter_url = models.URLField(null=True, blank=True, verbose_name="Candidate Twitter URL", max_length=255)
    candidate_instagram_url = models.URLField(null=True, blank=True, verbose_name="Candidate Instagram URL", max_length=255)
    candidate_youtube_url = models.URLField(null=True, blank=True, verbose_name="Candidate YouTube URL", max_length=255)

    completed_by_candidate = models.NullBooleanField(null=True, blank=True)

    def __unicode__(self):
        try:
            app = self.application_set.first()
            return str(app) + ' Questionnaire'
        except:
            return 'Questionnaire ' + str(self.pk)

    """Get response to question about issues, or None"""
    def _campaign_issues(self, *args, **kwargs):
        response = self.response_set.filter(
            question_id=settings.NOMINATIONS_QUESTION_ISSUES_ID,
        ).first()
        position = response.position if response else None
        return position
    campaign_issues = property(_campaign_issues)

    def save(self, skip_application_save=False, *args, **kwargs):
        super(Questionnaire, self).save(*args, **kwargs)

        if self.response_set.count() == 0:
            for q in Question.objects.all():
                self.response_set.create(question=q)

        '''
        Save the application(s) attached to a questionnaire when the
        questionnaire is saved.
        '''
        if not skip_application_save:
            for app in self.application_set.all():
                app.save()


class Question(models.Model):
    text = models.TextField(verbose_name="Question Text")
    include_multi_choice = models.BooleanField(default=True, verbose_name="Include Multiple Choice Selection")

    def __unicode__(self):
        return self.text


class Response(models.Model):
    QUESTIONNAIRE_CHOICES = (
        ('a', 'Strongly Agree'),
        ('c', 'Somewhat Agree'),
        ('d', 'Somewhat Disagree'),
        ('b', 'Strongly Disagree'),
    )
    questionnaire = models.ForeignKey(Questionnaire)
    question = models.ForeignKey(Question)
    response = models.CharField(max_length=1, blank=False, null=False, choices=QUESTIONNAIRE_CHOICES)
    position = models.TextField(max_length=1000, blank=True, null=True,verbose_name="Candidate's position on this issue:")

    def __unicode__(self):
        return unicode(self.question)


class Application(models.Model):
    """
    An application is a single submission for an endorsement. Each application
    consists of a group nomination and a candidate questionnaire, and has a
    many-to-one relationship with a group.
    """

    # See http://www.ncsl.org/research/elections-and-campaigns/primary-types.aspx
    primary_election_type_choices = (
        (1, 'Closed Primary'),
        (2, 'Partially Closed Primary'),
        (3, 'Partially Open Primary'),
        (4, 'Open to Unaffiliated Voters Primary'),
        (5, 'Open Primary'),
        (6, 'Top-Two Primary'),
        (7, 'Presidential Primary'),
        (99, 'Other'),
    )
    staff_recommendation_choices = (
        (1, 'Recommend to Endorse'),
        (2, 'Recommend Not to Endorse'),
        (3, 'No Recommendation'),
    )

    """Django User to use instead of legacy auth0 user"""
    auth_user = models.ForeignKey(
        User,
        blank=True,
        null=True,
    )
    fundraising_date_of_filing = models.DateField(
        blank=True,
        null=True,
        verbose_name='Filing Date for Fundraising Report'
    )
    fundraising_date_accessed = models.DateField(
        blank=True,
        null=True,
        verbose_name='Date fundraising information was accessed'
    )
    fundraising_source_url = models.URLField(
        blank=True,
        max_length=255,
        null=True,
        verbose_name='Fundraising Source URL'
    )
    """Legacy field for auth0 user id"""
    user_id = models.CharField(max_length=255, null=True, blank=True)
    create_dt = models.DateTimeField(auto_now_add=True)
    submitted_dt = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Submitted at'
    )

    nomination = models.OneToOneField(
        Nomination,
        on_delete=models.CASCADE,
        primary_key=False,
        null=True,
        blank=True,
        related_name='application',
        verbose_name='Group Nomination Form:',
    )
    primary_election_type = models.IntegerField(
        blank=True,
        choices=primary_election_type_choices,
        null=True,
    )
    questionnaire = models.ForeignKey(
        Questionnaire,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    group = models.ForeignKey(Group, to_field="group_id")

    rep_email = models.EmailField(
        null=True,
        blank=False,
        verbose_name="Contact Email",
        max_length=254
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
    rep_phone = PhoneNumberField(
        null=True,
        blank=True,
        verbose_name="Phone Number"
    )

    # TODO: change to foreign key and create new object for each new candidate,
    # implement autocomplete to  minimize duplicate candidates
    candidate_first_name = models.CharField(
        max_length=255,
        null=True,
        blank=False,
        verbose_name="Candidate First Name"
    )
    candidate_last_name = models.CharField(
        max_length=255,
        null=True,
        blank=False,
        verbose_name="Candidate Last Name"
    )
    candidate_office = models.CharField(
        null=True,
        max_length=255,
        blank=False,
        verbose_name="Candidate Office"
    )
    candidate_district = models.CharField(
        null=True,
        max_length=255,
        blank=True,
        verbose_name="Candidate District"
    )
    candidate_city = models.CharField(
        null=True,
        max_length=255,
        blank=True,
        verbose_name="Candidate City"
    )
    candidate_state = USStateField(max_length=2, null=True, blank=False)

    authorized_email = models.EmailField(
        null=True,
        blank=True,
        verbose_name="Authorized Email",
        max_length=254
    )

    # TODO TECH-840 convert statuses to integer fields
    STATUSES = (
        (
            'needs-group-form-and-questionnaire',
            'Needs Group Form and Questionnaire'
        ),
        ('needs-questionnaire', 'Needs Questionnaire'),
        ('needs-group-form', 'Needs Group Form'),
        ('incomplete', 'Needs Submission'),  # Deprecated as of 2019-01-08
        ('submitted', 'Submitted'),
        ('needs-research', 'Needs Research'),
        ('needs-staff-review', 'Needs Staff Review'),
        ('under-review', 'Under Review'),
        ('approved', 'Endorsed'),
        ('removed', 'Not Endorsed'),
        ('expired', 'Expired'),
        ('hold', 'Hold'),
    )

    # Statuses that signify whether a group can still edit an application
    EDITABLE_STATUSES = [
        'needs-group-form-and-questionnaire',
        'needs-questionnaire',
        'needs-group-form',
    ]

    status = models.CharField(
        max_length=64,
        choices=STATUSES,
        default='needs-group-form-and-questionnaire'
    )

    # Volunteer Data Entry
    vol_incumbent = models.NullBooleanField(
        null=True,
        blank=True,
        verbose_name='Incumbent?'
    )
    vol_dem_challenger = models.NullBooleanField(
        null=True,
        blank=True,
        verbose_name='If primary, who are the Democratic challengers?'
    )

    # TODO: rename to vol_other_candidates and remove old field from code
    # and db after a/b deploy issues are resolved
    # legacy field
    vol_other_progressives = models.TextField(
        null=True,
        blank=True,
        max_length=500,
        verbose_name='Other candidates running:',
        help_text='Please indicate party affiliation and other progressives. Max length 500 characters.'
    )
    vol_polling = models.TextField(
        null=True,
        blank=True,
        max_length=500,
        verbose_name='Polling:'
    )
    vol_endorsements = models.TextField(
        null=True,
        blank=True,
        max_length=500,
        verbose_name='Endorsements:'
    )
    vol_advantage = models.CharField(
        null=True,
        blank=True,
        max_length=50,
        verbose_name='Previous Election D% or R% Advantage:'
    )
    vol_turnout = models.CharField(
        null=True,
        blank=True,
        max_length=10,
        verbose_name='Previous Election Year Turnout:'
    )
    vol_win_number = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Win Number:'
    )
    vol_fundraising = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='How much money fundraised?'
    )
    #legacy field
    vol_opponent_fundraising = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='How much competitors have fundraised?'
    )
    vol_crimes = models.TextField(
        null=True,
        blank=True,
        max_length=500,
        verbose_name='Crimes or Scandals (please add links to source):'
    )
    vol_notes = models.TextField(
        null=True,
        blank=True,
        max_length=1000,
        verbose_name='Volunteer Notes:',
        help_text='Max length 1000 characters.'
    )

    # Staff only research fields
    CLASSIFICATIONS = (
        ('1', 'I'),
        ('2', 'II'),
        ('3', 'III'),
    )

    VET_STATUSES = (
        ('0', 'Pending'),
        ('1', 'Passed'),
        ('2', 'Failed'),
        ('3', 'Not Submitted'),
    )

    """TODO: remove?"""
    RECOMMENDATIONS = (
        ('1', 'Endorse'),
        ('2', 'Do Not Endorse')
    )

    classification_level = models.CharField(
        max_length=64,
        choices=CLASSIFICATIONS,
        default='1'
    )

    staff = models.CharField(
        max_length=64,
        blank=True,
        null=True,
    )

    """TODO: remove?"""
    recommendation = models.CharField(
        max_length=64,
        choices=RECOMMENDATIONS,
        default='1'
    )

    staff_bio = RichTextField(
        null=True,
        blank=True,
        verbose_name='Candidate Bio:',
        help_text='This will prepopulate from the candidate questionnaire if left blank.'
    )
    staff_recommendation = models.IntegerField(
        blank=True,
        choices=staff_recommendation_choices,
        null=True,
    )
    stand_out_information = RichTextField(
        blank=True,
        null=True,
    )

    state_of_the_race = RichTextField(
        null=True,
        blank=True,
        verbose_name='State of the Race:',
    )

    local_group_info = RichTextField(
        null=True,
        blank=True,
        verbose_name='OR Local Group Info:',
        help_text='This will prepopulate from the local group\'s endorsement process if left blank.'
    )

    staff_notes = RichTextField(
        null=True,
        blank=True,
        verbose_name='Staff Notes or Flags:',
        help_text='This will prepopulate from volunteer notes if left blank.'
    )

    vet_status = models.CharField(
        max_length=64,
        choices=VET_STATUSES,
        default='0'
    )

    vet = RichTextField(
        null=True,
        blank=True,
        verbose_name='Vet Details:',
    )

    local_support = RichTextField(
        null=True,
        blank=True,
        verbose_name='Local Support:',
        help_text='This will prepopulate from the local group\'s support question if left blank.'
    )
    def __unicode__(self):
        return str(self.group) + ' - ' + self.candidate_first_name + ' ' + self.candidate_last_name

    def _candidate_name(self):
        return self.candidate_first_name + ' ' + self.candidate_last_name
    candidate_name = property(_candidate_name)

    '''
    Group candidates by party and return list
    '''
    def _candidates_by_party(self):
        candidates = defaultdict(list)
        for application_candidate in self.applicationcandidate_set.order_by(
            'party',
            'first_name',
            'last_name'
        ):
            candidates[application_candidate.party].append(
                application_candidate
            )
        return candidates.items
    candidates_by_party = property(_candidates_by_party)

    def auto_populate_research_fields(self):
        """Auto-populate staff write-up fields from already present info"""
        if self.questionnaire:
            if self.questionnaire.candidate_bio and not self.staff_bio:
                self.staff_bio = self.questionnaire.candidate_bio

        if self.nomination:
            if self.nomination.group_nomination_process and not self.local_group_info:
                self.local_group_info = self.nomination.group_nomination_process

            # question ID 8 is "What actions will the group take
            # and how many people have agreed to volunteer/support?
            question = self.nomination.nominationresponse_set.filter(
                question_id=8
            ).first()

            if question and not self.local_support:
                self.local_support = question.response.encode('utf-8')

        if self.vol_notes and not self.staff_notes:
            self.staff_notes = self.vol_notes

    def create_related_objects(self):
        """Create related nomination and questionnaire for application."""
        if not self.nomination:
            self.nomination = Nomination.objects.create()

        if not self.questionnaire:
            self.questionnaire = Questionnaire.objects.create()

    def generate_application_status(self):
        """
        Returns a generated status based on completion of various items.

        Nomination is filled out by the group with basic information about
        the group and what it will do to help the candidate.

        Questionnaire is filled out by the candidate with basic information and
        in-depth policy positions.
        """

        if self.status in self.EDITABLE_STATUSES:
            if self.nomination.status == 'incomplete':
                if self.questionnaire.status == 'complete':
                    status = 'needs-group-form'
                else:
                    status = 'needs-group-form-and-questionnaire'
            else:
                # nomination complete
                if self.questionnaire.status == 'complete':
                    # questionnaire complete

                    """
                    Set as submitted if nomination + questionnaire are complete
                    """
                    status = 'submitted'

                else:
                    # needs questionaire
                    status = 'needs-questionnaire'
        else:
            status = self.status
        return status

    def is_editable(self):
        """Returns whether a group can edit this application."""

        if self.status in self.EDITABLE_STATUSES:
            return True
        else:
            return False

    def __unicode__(self):
        return str(self.group) + ' - ' + self.candidate_first_name + ' ' + self.candidate_last_name

    def save(self, *args, **kwargs):
        if not self.nomination or not self.questionnaire:
            self.create_related_objects()

        self.auto_populate_research_fields()

        self.status = self.generate_application_status()

        if self.status == 'submitted' and self.submitted_dt is None:
            self.submitted_dt = datetime.datetime.now()

        super(Application, self).save(*args, **kwargs)

    class Meta:
        permissions = (
            (
                "bulk_change_application_status",
                "Can bulk change status of applications"
            ),
            (
                "export_pdf_application",
                "Can export to pdf"
            ),
            (
                "admin_application",
                "Can admin override application data"
            ),
        )
        verbose_name = 'Candidate Application'


class ApplicationCandidate(models.Model):
    '''
    Information about candidates in a race related to an application
    '''
    party_choices = (
        (1, 'Democratic Party'),
        (2, 'Green Party'),
        (3, 'Independent/No Party Affiliation'),
        (4, 'Republican Party'),
        (5, 'Libertarian Party'),
        (6, 'Vermont Progressive Party'),
        (99, 'Other'),
    )
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    description = models.CharField(
        blank=True,
        max_length=500,
        null=True,
    )
    first_name = models.CharField(
        blank=True,
        max_length=255,
        null=True,
    )
    fundraising = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Cash on Hand'
    )
    last_name = models.CharField(
        blank=True,
        max_length=255,
        null=True,
    )
    party = models.IntegerField(
        blank=True,
        choices=party_choices,
        null=True,
    )
    website_url = models.URLField(
        blank=True,
        max_length=255,
        null=True,
    )

    def _name(self):
        if self.first_name and self.last_name:
            return self.first_name + ' ' + self.last_name
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return None
    name = property(_name)

    def __unicode__(self):
        return str(self.id) + (' ' + self.name if self.name else '')


class InitiativeApplication(models.Model):
    """Django User to use instead of legacy auth0 user"""
    auth_user = models.ForeignKey(
        User,
        blank=True,
        null=True,
    )
    """Legacy Auth0 user id"""
    user_id = models.CharField(max_length=255, null=True, blank=True)
    create_dt = models.DateTimeField(auto_now_add=True)
    submitted_dt = models.DateTimeField(null=True, blank=True, verbose_name = 'Submitted at')

    group = models.ForeignKey(Group, to_field="group_id")

    rep_email = models.EmailField(null=True, blank=False, verbose_name="Contact Email", max_length=254)
    rep_first_name = models.CharField(max_length=35, null=True, blank=False, verbose_name="First Name")
    rep_last_name = models.CharField(max_length=35, null=True, blank=False, verbose_name="Last Name")
    rep_phone = PhoneNumberField(null=True, blank=True, verbose_name="Phone Number")

    name = models.CharField(max_length=254,null=True,blank=False, verbose_name =" Initiative Name")
    election_date = models.DateField(verbose_name = 'Election Date', null = True, blank = False)
    website_url = models.URLField(null=True, blank=False, verbose_name="Initiative Website URL", max_length=255)
    volunteer_url = models.URLField(null=True, blank=True, verbose_name="Volunteer URL", max_length=255)
    donate_url = models.URLField(null=True, blank=True, verbose_name="Donate URL", max_length=255)
    city = models.CharField(max_length=254,null=True,blank=True)
    county = models.CharField(max_length=254,null=True,blank=True)
    state = USStateField(max_length=2, null=True, blank=False, verbose_name="State")
    description = models.TextField(max_length=500, blank=False, null=True, verbose_name = "What would the initiative do?")
    question = models.TextField(max_length=500, blank=True, null=True, verbose_name = "How will the question appear on the ballot?")
    vote = models.NullBooleanField(null=True, blank=True, verbose_name='How to vote:')
    additional_info = models.TextField(max_length=500, blank=True, null=True, verbose_name = "Any additional information you want to share?")

    LOCALITIES = (
       ('city', 'Citywide'),
       ('county', 'Countywide'),
       ('state', 'Statewide'),
    )

    locality = models.CharField(max_length=16, choices=LOCALITIES, default='state', verbose_name='Is this initiative:')

    STATUSES = (
       ('incomplete', 'Incomplete'),
       ('submitted', 'Submitted'),
       ('needs-research','Needs Research'),
       ('needs-staff-review', 'Needs Staff Review'),
       ('approved', 'Endorsed'),
       ('removed', 'Not Endorsed')
    )
    status = models.CharField(max_length=64, choices=STATUSES, default='submitted')

    def __unicode__(self):
        return str(self.group) + ' - ' + self.name

    def save(self, *args, **kwargs):
        if self.status == 'submitted' and self.submitted_dt is None:
            self.submitted_dt = datetime.datetime.now()

        super(InitiativeApplication, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Ballot Initiative Application'
