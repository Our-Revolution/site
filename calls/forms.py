from django import forms
from django.conf import settings
from django.forms import widgets
from .models import CallCampaign

CALLS_MAX_DISTANCE_MILES = settings.CALLS_MAX_DISTANCE_MILES
CALLS_MAX_LIST_SIZE = settings.CALLS_MAX_LIST_SIZE


class CallCampaignForm(forms.ModelForm):
    max_distance = forms.IntegerField(
        help_text="Max: %s miles" % CALLS_MAX_DISTANCE_MILES,
        label="Radius",
        max_value=CALLS_MAX_DISTANCE_MILES,
        min_value=1
    )
    max_recipients = forms.IntegerField(
        help_text="Max: %s contacts" % CALLS_MAX_LIST_SIZE,
        label="Max Number of Contacts",
        max_value=CALLS_MAX_LIST_SIZE,
        min_value=1
    )

    class Meta:
        fields = [
            'max_distance',
            'max_recipients',
            'postal_code',
            'script',
            'state_or_territory',
            'title',
        ]
        model = CallCampaign
        widgets = {
            'script': forms.Textarea(attrs={'rows': '14'}),
        }


class CallCampaignAdminForm(CallCampaignForm):
    class Meta:
        field_width = '640px'
        widgets = {
            'script': forms.Textarea(attrs={
                'rows': '14',
                'style': "width: %s" % field_width
            }),
        }
