from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Fieldset
from local_groups.models import Group
from .models import (
    Application,
    ApplicationCandidate,
    Nomination,
    NominationResponse,
    Questionnaire,
    Response,
    InitiativeApplication,
)
import os, requests


class DateInput(forms.DateInput):
    input_type = 'date'


class ApplicationForm(forms.ModelForm):
    agree = forms.BooleanField(label='I have read and agree to these terms.')

    #crispy forms
    def __init__(self, *args, **kwargs):
        super(ApplicationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_class = 'row'
        self.helper.form_id = 'application_form'

        self.helper.layout = Layout(
            Div(
                Div(
                    Field('agree', id='agree_field'),
                    css_class='clearfix fs-sm'
                ),
                HTML('<hr />'),
                HTML('<h3>Your Information</h3>'),
                Div(
                    Field('rep_first_name', wrapper_class='col-md-6'),
                    Field('rep_last_name', wrapper_class='col-md-6'),
                    Field('rep_phone', wrapper_class='col-md-6'),
                    Field('rep_email', wrapper_class='col-md-6'),
                    css_class='br3 pt20 f5f5f5-bg clearfix mb20'
                ),
                css_class="col-md-12",
            ),
            Div(
                HTML('<h3>Candidate Information</h3>'),
                Div(
                    Field('candidate_first_name', wrapper_class='col-md-6'),
                    Field('candidate_last_name', wrapper_class='col-md-6'),
                    Field('candidate_office', wrapper_class='col-md-6'),
                    Field('candidate_district', wrapper_class='col-md-6'),
                    Field('candidate_city', wrapper_class='col-md-6'),
                    Field('candidate_state', wrapper_class='col-md-6'),
                    css_class='br3 pt20 f5f5f5-bg clearfix mb20'
                ),
                css_class='col-md-12'
            ),
            Div(
                Submit(
                    'submit',
                    'Start a Nomination',
                    css_class='btn btn-success btn-block uppercase ls2',
                    css_id='submit_button'
                ),
                css_class='col-md-12'
            )
        )

    class Meta:
        model = Application
        fields = [
            'rep_email',
            'rep_first_name',
            'rep_last_name',
            'rep_phone',
            'candidate_first_name',
            'candidate_last_name',
            'candidate_office',
            'candidate_district',
            'candidate_city',
            'candidate_state'
        ]


class NominationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(NominationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.layout = Layout(
            Field('group_nomination_process', wrapper_class='fs16 mb0'),
        )

    class Meta:
        model = Nomination
        exclude = ['status']

class NominationResponseFormsetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(NominationResponseFormsetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_tag = False
        self.form_method = 'post'
        self.form_action = ''
        self.render_required_fields = True
        self.form_show_labels = False
        self.layout = Layout (
            Field('question',type='hidden'),
            Field('response',wrapper_class='mb0')
        )

NominationResponseFormset = forms.inlineformset_factory(Nomination, NominationResponse, exclude=[], extra=0, can_delete=False)


class QuestionnaireForm(forms.ModelForm):
    agree = forms.BooleanField(label='I have read and agree to these terms.')
    candidate_held_office = forms.BooleanField(
        label="Has the candidate ever held public office?",
        required=False,
    )
    candidate_is_member = forms.BooleanField(
        label="Is candidate a member of Our Revolution?",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(QuestionnaireForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.layout = Layout(
            Div(
                Div(
                    Field('agree', id='agree_field'),
                    css_class='clearfix fs-sm'
                ),
                HTML('<hr />'),
                HTML('<h3>Basic Candidate Information</h3>'),
                Div(
                    Field('candidate_first_name', wrapper_class='col-md-6'),
                    Field('candidate_last_name', wrapper_class='col-md-6'),
                    Field('candidate_bio', wrapper_class='col-md-12'),
                    Field('candidate_email', wrapper_class='col-md-6'),
                    Field('candidate_phone', wrapper_class='col-md-6'),
                    Field('candidate_office', wrapper_class='col-md-6'),
                    Field('candidate_district', wrapper_class='col-md-6'),
                    Field('candidate_city', wrapper_class='col-md-6'),
                    Field('candidate_state', wrapper_class='col-md-6'),
                    Field('general_election_date', wrapper_class='col-md-6'),
                    Field('primary_election_date', wrapper_class='col-md-6'),
                    Div(Field('candidate_held_office'), css_class='col-md-6'),
                    Div(Field('candidate_is_member'), css_class='col-md-6'),
                    Field('candidate_party', wrapper_class='col-md-6'),
                    css_class='pt20 br3 f5f5f5-bg mb20 clearfix',
                ),
                css_class='col-md-12'
            ),
            Div(
                HTML('<h3 class="mb0">Candidate Web & Social Information</h3><p>Please enter URLs in the format <a href="#">https://example.com</a>.</p>'),
                Div(
                    Field('candidate_website_url',wrapper_class='col-md-6'),
                    Field('candidate_volunteer_url',wrapper_class='col-md-6'),
                    Field('candidate_donate_url',wrapper_class='col-md-6'),
                    Field('candidate_facebook_url',wrapper_class='col-md-6'),
                    Field('candidate_twitter_url',wrapper_class='col-md-6'),
                    Field('candidate_instagram_url',wrapper_class='col-md-6'),
                    Field('candidate_youtube_url',wrapper_class='col-md-6'),
                    css_class='pt20 br3 f5f5f5-bg mb20 clearfix'
                ),
                css_class='col-md-12'
            )
        )

    class Meta:
        model = Questionnaire
        exclude = ['status']
        widgets = {
            'general_election_date': DateInput(),
            'primary_election_date': DateInput(),
        }


class QuestionnaireResponseFormsetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(QuestionnaireResponseFormsetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_tag = False
        self.form_method = 'post'
        self.form_action = ''
        self.render_required_fields = True

        # self.form_show_labels = False
        self.layout = Layout (
            Field('question',type='hidden'),
            Field('response'),
            Field('position',wrapper_class='mb0')
        )


QuestionnaireResponseFormset = forms.inlineformset_factory(
    Questionnaire,
    Response,
    exclude=[],
    extra=0,
    can_delete=False,
)

ApplicationCandidateFormset = forms.inlineformset_factory(
    Application,
    ApplicationCandidate,
    exclude=[],
    # extra=0,
    # can_delete=False,
)


class CandidateEmailForm(forms.Form):
    candidate_email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super(CandidateEmailForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_class = 'clearfix mb20'
        self.fields['candidate_email'].label = 'Candidate Email'
        self.helper.layout = Layout(
            Field('candidate_email'),
            Submit(
                'submit',
                'Send to Candidate',
                css_class='btn-block btn-success uppercase ls2',
            )
        )


class InitiativeApplicationForm(forms.ModelForm):
    agree = forms.BooleanField(label='I agree that members of the Group were given an unobstructive opportunity to weigh in on the nomination, that a majority of people in the group support the nominated initiative, and that there is significant support for the initiative and the Group is committed to aiding the initiative to victory.', required=True)

    LOCALITIES = (
       ('city', 'Citywide'),
       ('county', 'Countywide'),
       ('state', 'Statewide'),
    )

    locality = forms.ChoiceField(label='Is this initiative:',choices=LOCALITIES, initial='state')

    #crispy forms
    def __init__(self, *args, **kwargs):
        super(InitiativeApplicationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_class = 'row'
        self.helper.form_id = 'application_form'

        self.helper.layout = Layout(
            Div(
                HTML('<h3>Your Information</h3>'),
                Div(
                    Field('rep_first_name',wrapper_class='col-md-6'),
                    Field('rep_last_name',wrapper_class='col-md-6'),
                    Field('rep_phone',wrapper_class='col-md-6'),
                    Field('rep_email',wrapper_class='col-md-6'),
                    css_class = 'br3 pt20 f5f5f5-bg clearfix mb20'
                ),
                css_class="col-md-12",
            ),
            Div(
                HTML('<h3>Initiative Information</h3>'),
                Div(
                    Field('name',wrapper_class='col-md-12'),
                    Field('election_date',wrapper_class='col-md-6'),
                    Field('website_url',wrapper_class='col-md-6'),
                    Field('volunteer_url',wrapper_class='col-md-6'),
                    Field('donate_url',wrapper_class='col-md-6'),
                    Field('locality',wrapper_class='col-md-12',id='locality_field'),
                    Field('city',wrapper_class='col-md-6 city_field'),
                    Field('county',wrapper_class='col-md-6 county_field'),
                    Field('state',wrapper_class='col-md-6 state_field'),
                    Field('description',wrapper_class='col-md-12'),
                    Field('question',wrapper_class='col-md-12'),
                    Field('vote',wrapper_class='col-md-6'),
                    Field('additional_info',wrapper_class='col-md-12'),
                    css_class='br3 pt20 f5f5f5-bg clearfix mb20'
                ),
                css_class='col-md-12'
            ),
            Div(
                Field('agree',id='agree_field'),
                Submit(
                    'submit',
                    'Submit Nomination',
                    css_class='btn btn-success btn-block uppercase ls2 disabled',
                    css_id='submit_button'
                ),
                css_class='col-md-12'
            )
        )

    class Meta:
        model = InitiativeApplication
        fields = [
            'rep_email',
            'rep_first_name',
            'rep_last_name',
            'rep_phone',
            'name',
            'election_date',
            'website_url',
            'volunteer_url',
            'donate_url',
            'city',
            'county',
            'state',
            'description',
            'question',
            'vote',
            'additional_info',
        ]

        widgets = {
            'election_date': DateInput(),
        }


class ApplicationsStatusChangeForm(forms.Form):
    confirm = forms.BooleanField(required=True)


class PrioritySupportForm(forms.ModelForm):
    text_maxlength = 10
    textarea_maxlength = 1000
    textarea_rows = 8

    stand_out_information = forms.CharField(
        label="Stand out information:",
        max_length=textarea_maxlength,
        widget=forms.Textarea(attrs={'rows': textarea_rows})
    )
    state_of_the_race = forms.CharField(
        label="State of the Race:",
        max_length=textarea_maxlength,
        widget=forms.Textarea(attrs={'rows': textarea_rows})
    )
    vol_endorsements = forms.CharField(
        label="Endorsements:",
        max_length=textarea_maxlength,
        widget=forms.Textarea(attrs={'rows': textarea_rows})
    )
    vol_polling = forms.CharField(
        label="Polling:",
        max_length=textarea_maxlength,
        widget=forms.Textarea(attrs={'rows': textarea_rows})
    )
    vol_turnout = forms.CharField(
        label='Previous Election Year Turnout:',
        max_length=text_maxlength,
    )

    class Meta:
        fields = [
            'stand_out_information',
            'state_of_the_race',
            'vol_endorsements',
            'vol_polling',
            'vol_turnout',
        ]
        model = Application
