from django import forms
from django.conf import settings
from contacts.models import ContactListStatus
from .models import (
    call_campaign_statuses_skip_list_validation,
    CallCampaign,
    CallQuestion
)
import logging

logger = logging.getLogger(__name__)

CALLS_MAX_DISTANCE_MILES = settings.CALLS_MAX_DISTANCE_MILES
CALLS_MAX_LIST_SIZE = settings.CALLS_MAX_LIST_SIZE


class CallForm(forms.Form):
    call_uuid = forms.UUIDField(required=False, widget=forms.HiddenInput)
    exit_after_call = forms.BooleanField(required=False)
    opt_out = forms.TypedChoiceField(
        choices=[(None, '')] + [
            x.value for x in CallQuestion.opt_out.value[2]
        ],
        coerce=int,
        empty_value=None,
        label=CallQuestion.opt_out.value[1],
        required=False,
    )
    take_action = forms.TypedChoiceField(
        choices=[(None, '')] + [
            x.value for x in CallQuestion.take_action.value[2]
        ],
        coerce=int,
        empty_value=None,
        label=CallQuestion.take_action.value[1],
        required=False,
    )
    talk_to_contact = forms.TypedChoiceField(
        choices=[(None, '')] + [
            x.value for x in CallQuestion.talk_to_contact.value[2]
        ],
        coerce=int,
        empty_value=None,
        label=CallQuestion.talk_to_contact.value[1],
        required=False,
    )
    talk_to_contact_why_not = forms.TypedChoiceField(
        choices=[(None, '')] + [
            x.value for x in CallQuestion.talk_to_contact_why_not.value[2]
        ],
        coerce=int,
        empty_value=None,
        label=CallQuestion.talk_to_contact_why_not.value[1],
        required=False,
    )
    voice_message = forms.TypedChoiceField(
        choices=[(None, '')] + [
            x.value for x in CallQuestion.voice_message.value[2]
        ],
        coerce=int,
        empty_value=None,
        label=CallQuestion.voice_message.value[1],
        required=False,
    )


class CallCampaignForm(forms.ModelForm):
    caller_emails = forms.CharField(
        widget=forms.Textarea(attrs={'rows': '5'}),
        required=False
    )
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
            'caller_emails',
            'max_distance',
            'max_recipients',
            'postal_code',
            'script',
            'state_or_territory',
            'title',
        ]
        model = CallCampaign
        widgets = {
            'script': forms.Textarea(attrs={'rows': '14'})
        }

class CallCampaignUpdateForm(CallCampaignForm):
    max_distance = forms.IntegerField(disabled=True)
    max_recipients = forms.IntegerField(disabled=True)
    postal_code = forms.CharField(disabled=True)
    state_or_territory = forms.CharField(disabled=True)

class CallCampaignAdminForm(CallCampaignForm):

    def clean_status(self):
        """Check if status requires a valid Contact List attached"""
        status = self.cleaned_data['status']
        if status not in [
            x.value[0] for x in call_campaign_statuses_skip_list_validation
        ]:
            contact_list = self.instance.contact_list
            if contact_list is None or not (
                contact_list.status == ContactListStatus.complete.value[0]
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
