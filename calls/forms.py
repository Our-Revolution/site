from bsd.models import BSDProfile
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.forms import widgets
from django.forms.widgets import Widget
from django.forms.utils import flatatt
from django.utils.html import mark_safe
from .models import CallCampaign, CallProfile

CALLS_MAX_DISTANCE_MILES = settings.CALLS_MAX_DISTANCE_MILES
CALLS_MAX_LIST_SIZE = settings.CALLS_MAX_LIST_SIZE

class CommaSeparatedCallersTextArea(Widget):
    def render(self, name, value, attrs=None, renderer=None):
        final_attrs = self.build_attrs(attrs, {'type':'text', 'name':name})
        caller_emails = []

        if value is not None:
            for caller_id in value:
                callprofile = CallProfile.objects.get(pk=caller_id)
                user = callprofile.user
                caller_emails.append(str(user.email))

            value = ', '.join(caller_emails)
            if value:
                final_attrs['value'] = str(value)
        return mark_safe(u'<input%s />' % flatatt(final_attrs))

class ModelCommaSeparatedChoiceField(forms.ModelMultipleChoiceField):
    widget = CommaSeparatedCallersTextArea(
        attrs={
            'rows': '5',
            'placeholder': 'bob@example.com, sally@example.comm, tom@example.com'
        }
    )

    def clean(self, value):
        caller_ids = []

        if value is not None and value != '':
            value = [email.strip() for email in value.split(",")]

            for email in value:
                # TODO: support multiple accounts per email
                if User.objects.filter(email__iexact=email).exists():
                    user = User.objects.get(email__iexact=email)
                else:
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        password=None
                    )

                if not hasattr(user,'bsdprofile'):
                    BSDProfile.objects.create(user=user)

                if not hasattr(user,'callprofile'):
                    CallProfile.objects.create(user=user)

                caller_ids.append(user.callprofile.id)

        return super(ModelCommaSeparatedChoiceField, self).clean(caller_ids)

class CallCampaignForm(forms.ModelForm):
    callers = ModelCommaSeparatedChoiceField(
        queryset=CallProfile.objects.all(),
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
            'callers',
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
    class Meta:
        field_width = '640px'
        widgets = {
            'script': forms.Textarea(attrs={
                'rows': '14',
                'style': "width: %s" % field_width
            }),
        }
