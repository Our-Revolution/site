from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Fieldset
from local_groups.models import Group
from .models import Nomination, Application, NominationResponse, Questionnaire, Response
import os, requests


class ApplicationForm(forms.ModelForm):
    group_name = forms.CharField(label="Group Name")
    group = forms.ModelChoiceField(label="Group ID", to_field_name="group_id", \
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
                    'candidate_district','candidate_state']


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
                HTML('<h3>Candidate Information</h3>'),
                Div(
                    Field('candidate_first_name',wrapper_class='col-md-6'),
                    Field('candidate_last_name',wrapper_class='col-md-6'),
                    Field('candidate_email',wrapper_class='col-md-6'),
                    Field('candidate_phone',wrapper_class='col-md-6'),
                    Field('candidate_office',wrapper_class='col-md-6'),
                    Field('candidate_district',wrapper_class='col-md-6'),
                    Field('candidate_state',wrapper_class='col-md-6'),
                    css_class='pt20 br3 f5f5f5-bg mb20 clearfix'
                ),
                css_class='col-md-12'
            )
        )
        
    class Meta:
        model = Questionnaire
        exclude = ['status']

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
    group = forms.ModelChoiceField(label="Group ID", to_field_name="group_id", \
                        queryset=Group.objects.filter(status='approved'), widget=forms.NumberInput, \
                        error_messages={'invalid_choice': "We couldn't find a group with that ID - if you need help, email info@ourrevolution.com."})

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_class = 'row'
        self.helper.layout = Layout(
            Field('email', wrapper_class='col-md-8'),
            Field('group', wrapper_class='col-md-4'),
            Div(
                Submit('submit','Login',css_class='btn btn-block btn-primary uppercase ls2'),
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
