from django import forms
from .models import Event, Group
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    UsernameField,
)
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.forms import widgets
from django.utils.translation import gettext_lazy as _
from endorsements.models import Issue
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget
import os
import requests
import logging


logger = logging.getLogger(__name__)


class HTML5DateInput(widgets.DateInput):
    input_type = 'date'


class HTML5TimeInput(widgets.TimeInput):
    input_type = 'time'


class EventForm(forms.ModelForm):
    host_receive_rsvp_emails = forms.ChoiceField(
        choices=(
            (1, "YES, please email me when new people RSVP (recommended)"),
            (0, "No thanks")
        ),
        widget=forms.widgets.RadioSelect
    )
    public_phone = forms.ChoiceField(
        choices=(
            (1, '''
            YES, make my phone number visible to people viewing your event
            (recommended)
            '''),
            (0, "Please keep my number private")
        ),
        widget=forms.widgets.RadioSelect
    )

    class Meta:
        fields = [
            'event_type',
            'capacity',
            'contact_phone',
            'host_name',
            'name',
            'description',
            'duration_count',
            'duration_type',
            'host_receive_rsvp_emails',
            'public_phone',
            'start_day',
            'start_time',
            'start_time_zone',
            'venue_name',
            'venue_addr1',
            'venue_addr2',
            'venue_city',
            'venue_directions',
            'venue_state_or_territory',
            'venue_zip',
        ]
        model = Event
        widgets = {
            'description': forms.Textarea(attrs={'rows': '2'}),
            'start_day': HTML5DateInput(),
            'start_time': HTML5TimeInput(),
            'venue_directions': forms.Textarea(attrs={'rows': '2'}),
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


class GroupCreateForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Group
        exclude = (
            'slug', 'signup_date', 'status', 'point', 'group_id', 'group_type'
        )
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


class GroupPasswordResetForm(forms.Form):
    """
    Custom password reset form for Organizing Hub users

    Based on https://github.com/django/django/blob/stable/1.10.x/django/contrib/auth/forms.py#L295
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    field_order = ['new_password1', 'new_password2']
    new_password_max_length = 100
    new_password_min_length = 8
    new_password1 = forms.CharField(
        label=_("New password"),
        help_text='''
        For strong password use at least 15 characters and multiple character
        types.
        ''',
        max_length=new_password_max_length,
        min_length=new_password_min_length,
        widget=forms.PasswordInput,
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        max_length=new_password_max_length,
        min_length=new_password_min_length,
        strip=False,
        widget=forms.PasswordInput,
    )

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2


class GroupPasswordChangeForm(GroupPasswordResetForm):
    """
    Custom password change form for Organizing Hub users

    Based on https://github.com/django/django/blob/stable/1.10.x/django/contrib/auth/forms.py#L295
    """
    field_order = ['old_password', 'new_password1', 'new_password2']

    old_password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={'autofocus': ''}),
    )


class GroupPasswordResetRequestForm(PasswordResetForm):
    email = forms.EmailField(
        label=_("Group Leader Email"),
        max_length=254
    )

    # todo: bsd account exists, but has never logged into hub, no user in db
    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.
        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        active_users = User.objects.filter(email__iexact=email, is_active=True)
        return active_users


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
