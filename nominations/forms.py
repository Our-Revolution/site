from django import forms
from django.db import models
import os, requests

from models import Nomination, Application

class NewApplicationForm(forms.Form):
    rep_email = forms.EmailField(label="Group Representative Email")
    # full_name = forms.CharField(required=False, label="Your Full Name", help_text="Optional")
    # state = forms.ChoiceField(label="Invite me to a specific Slack channel", help_text="You can join others once you log in.",initial="C36GU58J0")
    # group_nomination_process = forms.CharField(max_length=500) 
    
    def __init__(self, *args, **kwargs):
        super(NewApplicationForm, self).__init__(*args, **kwargs)
        
    # required_css_class = 'required'

    class Meta:
        model = Application
        exclude = ('create_dt')
        widgets = {
            # 'rep_phone': PhoneNumberInternationalFallbackWidget(),
            # 'last_meeting': forms.DateInput(),
            # 'description': forms.Textarea(attrs={'rows':'5'}),
            # 'other_social': forms.Textarea(attrs={'rows':'2'}),
            # 'other_issues': forms.Textarea(attrs={'rows':'4'}),
            # 'group_nomination_process': forms.Textarea(attrs={'rows':'3'}),
            # 'issues': forms.CheckboxSelectMultiple
        }
