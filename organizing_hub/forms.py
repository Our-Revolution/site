from django import forms


class GroupLeaderSyncForm(forms.Form):
    confirm = forms.BooleanField(required=True)
