from django import forms
from django.utils.translation import gettext_lazy as _


class GroupAdminsForm(forms.Form):
    """
    Edit Group Admins for Local Group
    """
    email = forms.EmailField(label="Email Address")
    is_admin = forms.BooleanField(required=False)


class PasswordResetForm(forms.Form):
    """
    Custom password reset form for Organizing Hub users

    Based on https://github.com/django/django/blob/stable/1.10.x/django/contrib/auth/forms.py#L295
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    field_order = ['new_password1', 'new_password2']
    new_password_max_length = 100
    new_password_min_length = 8

    new_password1 = forms.CharField(
        label=_("New password"),
        help_text='''
        For strong password use at least 15 characters and multiple character
        types.
        ''',
        max_length=new_password_max_length,
        min_length=new_password_min_length,
        widget=forms.PasswordInput,
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        max_length=new_password_max_length,
        min_length=new_password_min_length,
        strip=False,
        widget=forms.PasswordInput,
    )

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2


class AccountCreateForm(PasswordResetForm):
    email_address = forms.EmailField(max_length=255)
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    postal_code = forms.CharField(max_length=12)


class PasswordChangeForm(PasswordResetForm):
    """
    Custom password change form for Organizing Hub users

    Based on https://github.com/django/django/blob/stable/1.10.x/django/contrib/auth/forms.py#L295
    """
    field_order = ['old_password', 'new_password1', 'new_password2']

    old_password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={'autofocus': ''}),
    )
