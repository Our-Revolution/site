from django import forms
from local_groups.models import Group
from phonenumber_field.widgets import PhoneNumberPrefixWidget, PhoneNumberInternationalFallbackWidget
from phonenumber_field.modelfields import PhoneNumberField


class GroupForm(forms.ModelForm):

    required_css_class = 'required'
    
    class Meta:
        model = Group
        exclude = ('slug','signup_date','status','point')
        widgets = {
            'rep_phone': PhoneNumberInternationalFallbackWidget(),
            'last_meeting': forms.DateInput(),
            'description': forms.Textarea(attrs={'rows':'5'}),
            'other_social': forms.Textarea(attrs={'rows':'2'}),
            'other_issues': forms.Textarea(attrs={'rows':'3'}),
            'constituency': forms.Textarea(attrs={'rows':'3'}),
            'issues': forms.CheckboxSelectMultiple
        }
