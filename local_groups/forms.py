from django import forms
from .models import Group
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.contrib.gis.geos import Point
from django.utils.translation import gettext_lazy as _
from endorsements.models import Issue
import os, requests


class GroupLoginForm(AuthenticationForm):
    username = UsernameField(
        label=_("Group Leader Email"),
        widget=forms.TextInput(attrs={'autofocus': True})
    )
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput,
    )
    error_messages = {
        'invalid_login': _(
            "The email address or password you entered is invalid."
        ),
        'inactive': _("This account is inactive."),
    }


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
