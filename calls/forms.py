from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.forms import widgets
# from django.forms.widgets import Widget
from .models import CallCampaign, CallProfile

CALLS_MAX_DISTANCE_MILES = settings.CALLS_MAX_DISTANCE_MILES
CALLS_MAX_LIST_SIZE = settings.CALLS_MAX_LIST_SIZE
#
# class CommaSeparatedTextArea(Widget):
#     def render(self, name, value, attrs=None, renderer=None):
#         # final_attrs = self.build_attrs(attrs, type='text', name=name)
#         objects = []
#         for each in value:
#
#             # try:
#             #     object = Tag.objects.get(pk=each)
#             # except:
#             #     continue
#             objects.append(object)
#
#         values = []
#         for each in objects:
#             values.append(str(each))
#         value = ', '.join(values)
#         if value: # only add 'value' if it's nonempty
#             final_attrs['value'] = force_unicode(value)
#         return mark_safe(u'<input%s />' % flatatt(final_attrs))

class ModelCommaSeparatedChoiceField(forms.ModelMultipleChoiceField):
    widget = forms.Textarea

    def clean(self, value):
        if value is not None:
            caller_ids = []

            value = [item.strip() for item in value.split(",")]

            for item in value:
                if User.objects.filter(email__iexact=item).exists():
                    user = User.objects.get(email__iexact=str(item))

                    if not hasattr(user,'callprofile'):
                        CallProfile.objects.create(user=user)
                else:
                    # create user
                    # create callprofile
                    print item + ' not a user'

                caller_ids.append(user.callprofile.id)

                value = caller_ids

        return super(ModelCommaSeparatedChoiceField, self).clean(value)

class CallCampaignForm(forms.ModelForm):
    max_distance = forms.IntegerField(
        help_text="Max: %s miles" % CALLS_MAX_DISTANCE_MILES,
        label="Radius",
        max_value=CALLS_MAX_DISTANCE_MILES,
        min_value=1
    )
    max_recipients = forms.IntegerField(
        help_text="Max: %s contacts" % CALLS_MAX_LIST_SIZE,
        label="Max Number of Contacts",
        max_value=CALLS_MAX_LIST_SIZE,
        min_value=1
    )
    callers = ModelCommaSeparatedChoiceField(
        queryset=CallProfile.objects.all()
    )

    class Meta:
        fields = [
            'callers',
            'max_distance',
            'max_recipients',
            'postal_code',
            'script',
            'state_or_territory',
            'title',
        ]
        model = CallCampaign
        widgets = {
            'script': forms.Textarea(attrs={'rows': '14'}),
        }


class CallCampaignAdminForm(CallCampaignForm):
    class Meta:
        field_width = '640px'
        widgets = {
            'script': forms.Textarea(attrs={
                'rows': '14',
                'style': "width: %s" % field_width
            }),
        }
