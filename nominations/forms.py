from django import forms
from django.db import models
import os, requests

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Fieldset

from models import Nomination, Application

class NewApplicationForm(forms.ModelForm):
    #crispy forms 
    def __init__(self, *args, **kwargs):
        super(NewApplicationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Start a Nomination'))
        self.helper.layout = Layout(
            Fieldset(
                'Group Representative',
                'rep_email',
                'rep_first_name',
                'rep_last_name',
                'rep_phone',
                css_class='mb20 mt20',
            ),
            Fieldset(
                'Candidate Information',
                'candidate_first_name',
                'candidate_last_name',
                'candidate_office',
                'candidate_state',
                css_class='mb20 mt20',
            ),
        )
            
    class Meta:
        model = Application
        fields = ['rep_email','rep_first_name','rep_last_name','rep_phone','candidate_first_name','candidate_last_name','candidate_office','candidate_state']
