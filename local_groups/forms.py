from django import forms
from .models import Group
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.contrib.gis.geos import Point
from django.utils.translation import gettext_lazy as _
from endorsements.models import Issue
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget
import os, requests


class GisForm(forms.ModelForm):
    issues = forms.ModelMultipleChoiceField(queryset=Issue.objects.all(), widget=forms.CheckboxSelectMultiple(), required=False)

    latitude = forms.DecimalField(
        min_value=-90,
        max_value=90,
        required=False,
    )
    longitude = forms.DecimalField(
        min_value=-180,
        max_value=180,
        required=False,
    )

    class Meta(object):
        model = Group
        exclude = []
        widgets = {'point': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        if args:    # If args exist
            data = args[0]
            if data['latitude'] and data['longitude']:    #If lat/lng exist
                latitude = float(data['latitude'])
                longitude = float(data['longitude'])
                data['point'] = Point(longitude, latitude)    # Set PointField
        try:
            coordinates = kwargs['instance'].point.tuple    #If PointField exists
            initial = kwargs.get('initial', {})
            initial['longitude'] = coordinates[0]    #Set Longitude from coordinates
            initial['latitude'] = coordinates[1]    #Set Latitude from coordinates
            kwargs['initial'] = initial
        except (KeyError, AttributeError):
            pass
        super(GisForm, self).__init__(*args, **kwargs)


class GroupCreateForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Group
        exclude = ('slug', 'signup_date', 'status', 'point')
        widgets = {
            'rep_phone': PhoneNumberInternationalFallbackWidget(),
            'last_meeting': forms.DateInput(),
            'description': forms.Textarea(attrs={'rows': '2'}),
            'other_social': forms.Textarea(attrs={'rows': '2'}),
            'other_issues': forms.Textarea(attrs={'rows': '2'}),
            'constituency': forms.Textarea(attrs={'rows': '2'}),
            'issues': forms.CheckboxSelectMultiple
        }


# Customize AuthenticationForm as needed
class GroupLoginForm(AuthenticationForm):
    username = UsernameField(
        label=_("Group Leader Email"),
        widget=forms.TextInput(attrs={'autofocus': True})
    )
    error_messages = {
        'invalid_login': _(
            "The email address or password you entered is invalid."
        ),
        'inactive': _("This account is inactive."),
    }


class GroupManageForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Group
        # exclude name and rep_email. include group_contact_email.
        fields = [
            'description',
            'city',
            'state',
            'county',
            'country',
            'postal_code',
            'size',
            'group_contact_email',
            'rep_first_name',
            'rep_last_name',
            'rep_phone',
            'rep_postal_code',
            'website_url',
            'facebook_url',
            'twitter_url',
            'instagram_url',
            'other_social',
            'types_of_organizing',
            'other_types_of_organizing',
            'issues',
            'other_issues',
            'constituency',
            'last_meeting',
            'recurring_meeting',
            'meeting_address_line1',
            'meeting_address_line2',
            'meeting_city',
            'meeting_state_province',
            'meeting_postal_code',
            'meeting_country',
        ]
        widgets = {
            'rep_phone': PhoneNumberInternationalFallbackWidget(),
            'last_meeting': forms.DateInput(),
            'description': forms.Textarea(attrs={'rows': '2'}),
            'other_social': forms.Textarea(attrs={'rows': '2'}),
            'other_issues': forms.Textarea(attrs={'rows': '2'}),
            'constituency': forms.Textarea(attrs={'rows': '2'}),
            'issues': forms.CheckboxSelectMultiple
        }


class SlackInviteForm(forms.Form):
    email = forms.EmailField(label="Your Email Address", help_text="We'll send your Slack invite here.")
    full_name = forms.CharField(required=False, label="Your Full Name", help_text="Optional")
    state = forms.ChoiceField(label="Invite me to a specific Slack channel", help_text="You can join others once you log in.",initial="C36GU58J0")

    def __init__(self, *args, **kwargs):

        super(SlackInviteForm, self).__init__(*args, **kwargs)

        channel_names = {
            'gis-nerdery': 'GIS Nerdery',
            'nc-research': 'NC Research',
            'techprojects': 'Tech Projects',
        }

        # fetch Slack channels
        req = requests.get("https://slack.com/api/channels.list?token=%s" % os.environ['LOCAL_OR_ORGANIZING_API_TOKEN'])
        channel_choices = [(c['id'], channel_names.get(c['name'], c['name'].replace('_', ' ').title())) for c in req.json()['channels']]

        channel_choices.insert(0, (None, 'None'))

        self.fields['state'].choices = channel_choices
