from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Fieldset
from local_groups.models import Group
from .models import Nomination, Application, NominationResponse, Questionnaire, Response, InitiativeApplication
import os, requests

class DateInput(forms.DateInput):
    input_type = 'date'

class ApplicationForm(forms.ModelForm):
    group_name = forms.CharField(label="Group Name")
    group = forms.ModelChoiceField(label="4 Digit Group ID (ex. 0413)", to_field_name="group_id", \
                        queryset=Group.objects.filter(status='approved'), widget=forms.NumberInput, \
                        error_messages={'invalid_choice': "We couldn't find a group with that ID - if you need help, email info@ourrevolution.com."})
    agree = forms.BooleanField(label='I agree that members of the Group were given an unobstructive opportunity to weigh in on the nomination, that a majority of people in the group support the nominated candidate over any other candidates in the election, and that there is significant support for the candidate and the Group is committed to aiding the progressive champion to victory.', required=True)

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
                HTML('<h3>Your Group Information</h3>'),
                Div(
                    Field('group_name',wrapper_class='col-md-8'),
                    Field('group',wrapper_class='col-md-4'),
                    Field('rep_first_name',wrapper_class='col-md-6'),
                    Field('rep_last_name',wrapper_class='col-md-6'),
                    Field('rep_phone',wrapper_class='col-md-6'),
                    Field('rep_email',wrapper_class='col-md-6'),
                    css_class = 'br3 pt20 f5f5f5-bg clearfix mb20'
                ),
                css_class="col-md-12",
            ),
            Div(
                HTML('<h3>Candidate Information</h3>'),
                Div(
                    Field('candidate_first_name',wrapper_class='col-md-6'),
                    Field('candidate_last_name',wrapper_class='col-md-6'),
                    Field('candidate_office',wrapper_class='col-md-6'),
                    Field('candidate_district',wrapper_class='col-md-6'),
                    Field('candidate_city',wrapper_class='col-md-6'),
                    Field('candidate_state',wrapper_class='col-md-6'),
                    css_class='br3 pt20 f5f5f5-bg clearfix mb20'
                ),
                css_class='col-md-12'
            ),
            Div(
                Field('agree',id='agree_field'),
                Submit(
                    'submit',
                    'Start a Nomination',
                    css_class='btn btn-primary btn-block uppercase ls2 disabled',
                    css_id='submit_button'
                ),
                css_class='col-md-12'
            )
        )

    class Meta:
        model = Application
        fields = ['group','rep_email','rep_first_name','rep_last_name','rep_phone',
                    'candidate_first_name','candidate_last_name','candidate_office',
                    'candidate_district','candidate_city','candidate_state']


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
    def __init__(self, *args, **kwargs):
        super(QuestionnaireForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.layout = Layout(
            Div(
                HTML('<h3>Basic Candidate Information</h3>'),
                Div(
                    Field('candidate_first_name',wrapper_class='col-md-6'),
                    Field('candidate_last_name',wrapper_class='col-md-6'),
                    Field('candidate_bio',wrapper_class='col-md-12'),
                    Field('candidate_email',wrapper_class='col-md-6'),
                    Field('candidate_phone',wrapper_class='col-md-6'),
                    Field('candidate_office',wrapper_class='col-md-6'),
                    Field('candidate_district',wrapper_class='col-md-6'),
                    Field('candidate_party',wrapper_class='col-md-6'),
                    Field('candidate_held_office',wrapper_class='col-md-6'),
                    Field('candidate_city',wrapper_class='col-md-6'),
                    Field('candidate_state',wrapper_class='col-md-6'),
                    Field('general_election_date',wrapper_class='col-md-6'),
                    Field('primary_election_date',wrapper_class='col-md-6'),
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
            'primary_election_date': DateInput()
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

QuestionnaireResponseFormset = forms.inlineformset_factory(Questionnaire, Response, exclude=[], extra=0, can_delete=False)

class LoginForm(forms.Form):
    email = forms.EmailField()
    group = forms.ModelChoiceField(label="4 Digit Group ID (ex. 0413)", to_field_name="group_id", \
                        queryset=Group.objects.filter(status='approved'), widget=forms.NumberInput, \
                        error_messages={'invalid_choice': "We couldn't find a group with that ID - if you need help, email info@ourrevolution.com."})

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_class = 'row'
        self.fields['group'].label = '4 Digit Group ID (ex. 0413)'
        self.fields['email'].label = 'Group Representative Email'
        self.helper.layout = Layout(
            Field('email', wrapper_class='col-md-8'),
            Field('group', wrapper_class='col-md-4'),
            Div(
                Submit('submit','Get Started',css_class='btn btn-block btn-primary uppercase ls2'),
                css_class='col-md-12'
            )
        )

class SubmitForm(forms.Form):
    agree = forms.BooleanField(label='I have read and agree to these terms.', required=True)

    def __init__(self, *args, **kwargs):
        super(SubmitForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_id = 'submit_form'
        self.helper.layout = Layout(
            Field('agree',id='agree_field'),
            Submit('submit','Submit',css_class='btn-block uppercase ls2 disabled',css_id='submit_button')
        )

class CandidateEmailForm(forms.Form):
    candidate_email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super(CandidateEmailForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_class = 'col-md-12 clearfix mb20'
        self.fields['candidate_email'].label = 'Candidate Email'
        self.helper.layout = Layout(
            Field('candidate_email'),
            Submit('submit','Send to Candidate',css_class='btn-block uppercase ls2')
        )

class CandidateLoginForm(forms.Form):
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super(CandidateLoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_class = 'row'
        self.helper.layout = Layout(
            Field('email', wrapper_class='col-md-12'),
            Div(
                Submit('submit','Get Started',css_class='btn btn-block btn-primary uppercase ls2'),
                css_class='col-md-12'
            )
        )

class CandidateSubmitForm(forms.Form):
    agree = forms.BooleanField(label='I have read and agree to these terms.', required=True)

    def __init__(self, *args, **kwargs):
        super(CandidateSubmitForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_id = 'submit_form'
        self.helper.layout = Layout(
            Field('agree',id='agree_field'),
            Submit('submit','Submit',css_class='btn-block uppercase ls2 disabled',css_id='submit_button')
        )

class InitiativeApplicationForm(forms.ModelForm):
    group_name = forms.CharField(label="Group Name")
    group = forms.ModelChoiceField(label="4 Digit Group ID (ex. 0413)", to_field_name="group_id", \
                        queryset=Group.objects.filter(status='approved'), widget=forms.NumberInput, \
                        error_messages={'invalid_choice': "We couldn't find a group with that ID - if you need help, email info@ourrevolution.com."})
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
                HTML('<h3>Your Group Information</h3>'),
                Div(
                    Field('group_name',wrapper_class='col-md-8'),
                    Field('group',wrapper_class='col-md-4'),
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
                    css_class='btn btn-primary btn-block uppercase ls2 disabled',
                    css_id='submit_button'
                ),
                css_class='col-md-12'
            )
        )

    class Meta:
        model = InitiativeApplication
        fields = ['group','rep_email','rep_first_name','rep_last_name','rep_phone','name','election_date','website_url','volunteer_url','donate_url','city','county','state','description','question','vote','additional_info']

        widgets = {
            'election_date': DateInput(),
        }

class QuestionnaireExportForm(forms.ModelForm):
    recommendation_author = forms.CharField(label="Recommendation Written By:",initial="Erika Andiola")
    RECOMMENDATIONS = (
       ('endorse', 'Endorse'),
       ('no-endorse', 'Do Not Endorse'),
    )

    staff_recommendation = forms.ChoiceField(label='Staff Recommendation:',choices=RECOMMENDATIONS, initial='endorse')
    candidate_held_office = forms.BooleanField(label="Has the candidate ever held public office?", initial=False, required=False)

    #crispy forms
    def __init__(self, *args, **kwargs):
        super(QuestionnaireExportForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_class = 'row'
        self.helper.form_id = 'questionnaire_form'
        self.helper.form_tag = False
        self.fields['candidate_email'].required = False

        self.helper.layout = Layout(
            Div(
                Div(
                    Field('recommendation_author',wrapper_class='col-md-7'),
                    Field('staff_recommendation',wrapper_class='col-md-5'),
                    css_class = 'br3 pt20 f5f5f5-bg clearfix mb20'
                ),
                css_class="col-md-12",
            ),
            Div(
                HTML('<h3>Candidate Information</h3>'),
                Div(
                    Field('candidate_first_name',wrapper_class='col-md-6'),
                    Field('candidate_last_name',wrapper_class='col-md-6'),
                    Field('candidate_bio',wrapper_class='col-md-12'),
                    Field('candidate_office',wrapper_class='col-md-6'),
                    Field('candidate_district',wrapper_class='col-md-6'),
                    Field('candidate_city',wrapper_class='col-md-6'),
                    Field('candidate_state',wrapper_class='col-md-6'),
                    Field('candidate_party',wrapper_class='col-md-6'),
                    Field('candidate_held_office',wrapper_class='col-md-12'),
                    css_class='br3 pt20 f5f5f5-bg clearfix mb20'
                ),
                css_class='col-md-12'
            ),
            Div(
                HTML('<h3>Election Information</h3>'),
                Div(
                    Field('primary_election_date',wrapper_class='col-md-6'),
                    Field('general_election_date',wrapper_class='col-md-6'),
                    css_class='br3 pt20 f5f5f5-bg clearfix mb20'
                ),
                css_class='col-md-12'
            ),
        )

    class Meta:
        model = Questionnaire
        exclude = ()

GroupFormset = forms.inlineformset_factory(Group, Application, exclude=[], extra=0, can_delete=False)

#could have/should have probably done this with formsets
class ApplicationExportForm(forms.ModelForm):
    #crispy forms
    def __init__(self, *args, **kwargs):
        super(ApplicationExportForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_class = 'row'
        self.helper.form_id = 'application_form'
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Div(
                HTML('<h3>State of the Race</h3>'),
                Div(
                    Field('vol_incumbent',wrapper_class='col-md-6'),
                    Field('vol_other_progressives',wrapper_class='col-md-12'),
                    Field('vol_polling',wrapper_class='col-md-12'),
                    Field('vol_endorsements',wrapper_class='col-md-12'),
                    Field('vol_advantage',wrapper_class='col-md-6'),
                    Field('vol_turnout',wrapper_class='col-md-6'),
                    Field('vol_win_number',wrapper_class='col-md-6'),
                    Field('vol_fundraising',wrapper_class='col-md-6'),
                    Field('vol_opponent_fundraising',wrapper_class='col-md-6'),
                    Field('vol_crimes',wrapper_class='col-md-12'),
                    Field('vol_notes',wrapper_class='col-md-12'),
                    css_class = 'br3 pt20 f5f5f5-bg clearfix mb20'
                ),
                css_class="col-md-12",
            ),
        )

    class Meta:
        model = Application
        exclude = ()
