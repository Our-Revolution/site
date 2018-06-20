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

    # required_css_class = 'required'
    # group_id = forms.CharField(
    #     disabled=True,
    #     label=_("Group ID"),
    # )
    # name = forms.CharField(
    #     disabled=True,
    #     help_text='To change Group Name, contact %s' % settings.ORGANIZING_EMAIL,
    # )
    # rep_email = forms.CharField(
    #     disabled=True,
    #     label=_("Group leader email"),
    #     help_text='To change Group Leader Email, contact %s' % settings.ORGANIZING_EMAIL,
    # )

    class Meta:
        model = EventPromotion
        fields = [
            'message',
            'subject',
            'max_recipients',

        ]
        widgets = {
            # 'rep_phone': PhoneNumberInternationalFallbackWidget(),
            # 'last_meeting': forms.DateInput(),
            'message': forms.Textarea(attrs={'rows': '8'}),
        }
