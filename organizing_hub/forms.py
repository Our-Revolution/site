# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.forms import widgets
from django.utils.translation import gettext_lazy as _
from bsd.models import Account, BSDEvent

ORGANIZING_EMAIL = settings.ORGANIZING_EMAIL

new_password_max_length = 100
new_password_min_length = 8
new_password_help_text = '''
For strong password use at least 15 characters and multiple character types.
'''


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
