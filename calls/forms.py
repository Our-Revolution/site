from django import forms
from django.conf import settings
from django.forms import widgets
from contacts.models import ContactListStatus
from .models import (
    call_campaign_statuses_skip_list_validation,
    CallCampaign,
    CallQuestion,
)
import logging

logger = logging.getLogger(__name__)

CALLS_MAX_DISTANCE_MILES = settings.CALLS_MAX_DISTANCE_MILES
CALLS_MAX_LIST_SIZE = settings.CALLS_MAX_LIST_SIZE


class CallForm(forms.Form):
    call_uuid = forms.UUIDField(required=False, widget=forms.HiddenInput)
    exit_after_call = forms.BooleanField(required=False)
    take_action = forms.TypedChoiceField(
        choices=[(None, '')] + [
            x.value for x in CallQuestion.take_action.value[2]
        ],
        coerce=int,
        empty_value=None,
        label='Did the contact want to take action?',
        required=False,
    )
    talk_to_contact = forms.TypedChoiceField(
        choices=[(None, '')] + [
            x.value for x in CallQuestion.talk_to_contact.value[2]
        ],
        coerce=int,
        empty_value=None,
        label='Did you talk to the contact?',
        required=False,
    )
    talk_to_contact_why_not = forms.TypedChoiceField(
        choices=[(None, '')] + [
            x.value for x in CallQuestion.talk_to_contact_why_not.value[2]
        ],
        coerce=int,
        empty_value=None,
        label='If you did not talk to the contact, why not?',
        required=False,
    )
    voice_message = forms.TypedChoiceField(
        choices=[(None, '')] + [
            x.value for x in CallQuestion.voice_message.value[2]
        ],
        coerce=int,
        empty_value=None,
        label='Did you leave a voice message?',
        required=False,
    )


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

    def clean_status(self):
        """Check if status requires a valid Contact List attached"""
        status = self.cleaned_data['status']
        if status not in [
            x.value[0] for x in call_campaign_statuses_skip_list_validation
        ]:
            contact_list = self.instance.contact_list
            if contact_list is None or not (
                contact_list.status == ContactListStatus.complete
            ) or not (
                contact_list.contacts.count() > 0
            ):
                raise forms.ValidationError(self.fields['status'].help_text)
        return status

    class Meta:
        field_width = '640px'
        widgets = {
            'script': forms.Textarea(attrs={
                'rows': '14',
                'style': "width: %s" % field_width
            }),
        }
