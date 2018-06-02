from django import forms
from django.utils.translation import gettext_lazy as _


class GroupAdminsForm(forms.Form):
    """
    Edit Group Admins for Local Group
    """
    email = forms.EmailField()
    is_admin = forms.BooleanField(label=_("""
        Check box to add Group Admin role for email. Uncheck to remove. Submit
        when done.
    """))
