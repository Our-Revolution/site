from django import forms


class GroupAdminsForm(forms.Form):
    """
    Edit Group Admins for Local Group
    """
    email = forms.EmailField(label="Email Address")
    is_admin = forms.BooleanField(required=False)