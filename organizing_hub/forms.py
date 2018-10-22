# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from bsd.api import BSD
from bsd.models import BSDProfile
from django import forms
from django.conf import settings
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm as AuthPasswordResetRequestForm,
    UsernameField
)
from django.contrib.auth.models import User
from django.forms import widgets
from django.utils.translation import gettext_lazy as _
from bsd.models import Account, BSDEvent

import logging
ORGANIZING_EMAIL = settings.ORGANIZING_EMAIL

new_password_max_length = 100
new_password_min_length = 8
new_password_help_text = '''
For strong password use at least 15 characters and multiple character types.
'''

# Get bsd api
bsdApi = BSD().api

logger = logging.getLogger(__name__)


class HTML5DateInput(widgets.DateInput):
    input_type = 'date'


class HTML5TimeInput(widgets.TimeInput):
    input_type = 'time'


class EventForm(forms.ModelForm):
    capacity = forms.IntegerField(
        help_text="Including guests. Leave 0 for unlimited.",
        label="Capacity Limit",
        min_value=0,
    )
    """Duration form field should be required and positive"""
    duration_count = forms.IntegerField(min_value=1)
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
        model = BSDEvent
        widgets = {
            'description': forms.Textarea(attrs={'rows': '2'}),
            'start_day': HTML5DateInput(),
            'start_time': HTML5TimeInput(),
            'venue_directions': forms.Textarea(attrs={'rows': '2'}),
        }


class EventUpdateForm(EventForm):
    start_day = forms.DateField(
        disabled=True,
        label="Date",
        help_text='To change Date, contact %s' % ORGANIZING_EMAIL,
    )
    start_time = forms.TimeField(
        disabled=True,
        label="Start Time",
        help_text='To change Start Time, contact %s' % ORGANIZING_EMAIL,
    )


class GroupAdminsForm(forms.Form):
    """
    Edit Group Admins for Local Group
    """
    email = forms.EmailField(label="Email Address")
    is_admin = forms.BooleanField(required=False)


# Customize AuthenticationForm as needed
class OrganizingHubLoginForm(AuthenticationForm):
    username = UsernameField(
        label=_("Email Address"),
        widget=forms.TextInput(attrs={'autofocus': True}),
        help_text='''
            This can be any email address with an Our Revolution account. To
            manage your group or nominate candidates, use a registered group
            leader or group admin email.
        '''
    )
    error_messages = {
        'invalid_login': _(
            "The email address or password you entered is invalid."
        ),
        'inactive': _("This account is inactive."),
    }


class PasswordResetForm(forms.Form):
    """
    Custom password reset form for Organizing Hub users

    Based on https://github.com/django/django/blob/stable/1.10.x/django/contrib/auth/forms.py#L295
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    field_order = ['new_password1', 'new_password2']

    new_password1 = forms.CharField(
        label=_("New password"),
        help_text=new_password_help_text,
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


class PasswordResetRequestForm(AuthPasswordResetRequestForm):
    email = forms.EmailField(
        label=_("Email Address"),
        max_length=254
    )

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.
        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """

        users = User.objects.filter(email__iexact=email)

        """If user isn't in db, check for bsd account"""
        if not users:
            try:
                '''
                Get constituents from BSD by email

                https://github.com/bluestatedigital/bsd-api-python#raw-api-method
                '''
                api_call = '/cons/get_constituents_by_email'
                api_params = {'emails': email}
                apiResult = bsdApi.doRequest(api_call, api_params)

                """Validate response"""
                assert apiResult.http_status is 200
                tree = ElementTree().parse(StringIO(apiResult.body))
                cons = tree.find('cons')
                assert cons is not None
                cons_id = cons.get('id')
                assert cons_id is not None
                assert cons.findtext('has_account') == "1"
                assert cons.findtext('is_banned') == "0"

                """Create user in db for valid BSD account"""
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=None
                )
                BSDProfile.objects.create(cons_id=cons_id, user=user)

                """Return new user"""
                users = [user]

            except AssertionError:
                pass

        return users

class AccountForm(forms.ModelForm, PasswordResetForm):
    """Max lengths based on bsd api"""
    new_password1 = forms.CharField(
        label=_("Password"),
        help_text=new_password_help_text,
        max_length=new_password_max_length,
        min_length=new_password_min_length,
        widget=forms.PasswordInput,
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_("Password confirmation"),
        max_length=new_password_max_length,
        min_length=new_password_min_length,
        strip=False,
        widget=forms.PasswordInput,
    )

    class Meta:
        fields = [
            'email_address',
            'first_name',
            'last_name',
            'new_password1',
            'new_password2',
            'postal_code',
        ]
        model = Account


class PasswordChangeForm(PasswordResetForm):
    """
    Custom password change form for Organizing Hub users

    Based on https://github.com/django/django/blob/stable/1.10.x/django/contrib/auth/forms.py#L295
    """
    field_order = ['old_password', 'new_password1', 'new_password2']

    old_password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={'autofocus': ''}),
    )
