from django import forms
from .models import EventPromotion


class EventPromotionForm(forms.ModelForm):
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
            'volunteer_count',

        ]
        # widgets = {
        #     'rep_phone': PhoneNumberInternationalFallbackWidget(),
        #     'last_meeting': forms.DateInput(),
        #     'description': forms.Textarea(attrs={'rows': '2'}),
        #     'other_social': forms.Textarea(attrs={'rows': '2'}),
        #     'other_issues': forms.Textarea(attrs={'rows': '2'}),
        #     'constituency': forms.Textarea(attrs={'rows': '2'}),
        #     'issues': forms.CheckboxSelectMultiple
        # }
