from django import forms
from django.db import models
import os, requests

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Fieldset

from models import Nomination, Application

class NewApplicationForm(forms.ModelForm):
    group_name = forms.CharField(label="Group Name")
    group_id = forms.CharField(label='Group ID')
    
    #crispy forms 
    def __init__(self, *args, **kwargs):
        super(NewApplicationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_class = 'row'
        
        self.helper.layout = Layout(
            Div(
                HTML('<div class="col-md-12"><h2>Your Group Information</h2></div>'),
                Div(
                    Field('group_name',wrapper_class='col-md-8'),
                    Field('group_id',wrapper_class='col-md-4'),
                    Field('rep_first_name',wrapper_class='col-md-6'),
                    Field('rep_last_name',wrapper_class='col-md-6'),
                    Field('rep_phone',wrapper_class='col-md-6'),
                    Field('rep_email',wrapper_class='col-md-6'),
                ),
                css_class="mb20 clearfix",
            ),
            Div(
                HTML('<div class="col-md-12"><h2>Candidate Information</h2></div>'),
                Div(
                    Field('candidate_first_name',wrapper_class='col-md-6'),
                    Field('candidate_last_name',wrapper_class='col-md-6'),
                    Field('candidate_office',wrapper_class='col-md-6'),
                    Field('candidate_state',wrapper_class='col-md-6'),
                ),
                css_class='mb_20 clearfix'
            ),
            Div(
                Submit(
                    'submit',
                    'Start a Nomination',
                    css_class='btn btn-primary btn-block uppercase ls2'
                ),
                css_class='col-md-12'
            )
        )
            
    class Meta:
        model = Application
        fields = ['group_name','group_id','rep_email','rep_first_name','rep_last_name','rep_phone','candidate_first_name','candidate_last_name','candidate_office','candidate_state']
