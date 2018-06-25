from django import forms
from django.conf import settings
from .models import EventPromotion


EVENTS_PROMOTE_MAX = settings.EVENTS_PROMOTE_MAX


class EventPromotionForm(forms.ModelForm):
    promote_max = EVENTS_PROMOTE_MAX
    max_recipients = forms.IntegerField(
        label="Please send this to how many nearby supporters",
        max_value=promote_max,
        min_value=1
    )

    class Meta:
        model = EventPromotion
        fields = [
            'message',
            'subject',
            'max_recipients',

        ]
        widgets = {
            'message': forms.Textarea(attrs={'rows': '8'}),
        }


class EventPromotionAdminForm(EventPromotionForm):
    class Meta:
        field_width = '640px'
        fields = '__all__'
        widgets = {
            'subject': forms.TextInput(attrs={
                'style': "width: %s" % field_width
            }),
            'message': forms.Textarea(attrs={
                'rows': '20',
                'style': "width: %s" % field_width
            }),
        }
