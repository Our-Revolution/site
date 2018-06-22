from django import forms
from django.forms import widgets
from .models import BSDEvent
import logging

logger = logging.getLogger(__name__)


class HTML5DateInput(widgets.DateInput):
    input_type = 'date'


class HTML5TimeInput(widgets.TimeInput):
    input_type = 'time'


class BSDEventForm(forms.ModelForm):
    capacity = forms.IntegerField(
        help_text="Including guests. Leave 0 for unlimited.",
        label="Capacity Limit",
        min_value=0,
    )
    duration_count = forms.IntegerField(min_value=0)
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
