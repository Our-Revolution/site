from django import forms
from django.conf import settings
from .models import Group
from django.contrib.gis.geos import Point
from django.forms import widgets
from django.utils.translation import gettext_lazy as _
from StringIO import StringIO
from xml.etree.ElementTree import ElementTree
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
            data = args[0].copy()  # Copy to make it mutable
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


class GroupLeaderSyncForm(forms.Form):
    confirm = forms.BooleanField(required=True)


class GroupManageForm(forms.ModelForm):
    required_css_class = 'required'
    group_id = forms.CharField(
        disabled=True,
        label=_("Group ID"),
    )
    name = forms.CharField(
        disabled=True,
        help_text='To change Group Name, contact %s' % settings.ORGANIZING_EMAIL,
    )
    rep_email = forms.CharField(
        disabled=True,
        label=_("Group leader email"),
        help_text='To change Group Leader Email, contact %s' % settings.ORGANIZING_EMAIL,
    )

    class Meta:
        model = Group
        fields = [
            'name',
            'group_id',
            'description',
            'city',
            'state',
            'county',
            'country',
            'postal_code',
            'size',
            'rep_email',
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
