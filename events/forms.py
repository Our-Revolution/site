from django import forms
from django.conf import settings
from .models import EventPromotion, message_max_length


EVENTS_PROMOTE_MAX_LIST_SIZE = settings.EVENTS_PROMOTE_MAX_LIST_SIZE

field_width = '640px'
message_max_length_local_group = message_max_length / 2
message_max_length_admin = message_max_length


class EventPromotionForm(forms.ModelForm):
    promote_max = EVENTS_PROMOTE_MAX_LIST_SIZE
    max_recipients = forms.IntegerField(
        label="Please send this to how many nearby supporters",
        max_value=promote_max,
        min_value=1
    )
    message = forms.CharField(
        max_length=message_max_length_local_group,
        widget=forms.Textarea(attrs={'rows': 8})
    )

    class Meta:
        model = EventPromotion
        fields = [
            'message',
            'subject',
            'max_recipients',

        ]


class EventPromotionAdminForm(EventPromotionForm):
    message = forms.CharField(
        max_length=message_max_length_admin,
        widget=forms.Textarea(attrs={
            'rows': '20',
            'style': "width: %s" % field_width
        })
    )

    class Meta:
        fields = '__all__'
        widgets = {
            'subject': forms.TextInput(attrs={
                'style': "width: %s" % field_width
            }),
        }
