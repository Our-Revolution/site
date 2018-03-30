from __future__ import unicode_literals
from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from allauth.utils import build_absolute_uri


class AccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        """Constructs the email confirmation (activation) url.
        Note that if you have architected your system such that email
        confirmations are sent outside of the request context `request`
        can be `None` here.
        """
        url = reverse(
            "groups-verify-email-confirm",
            args=[emailconfirmation.key])
        ret = build_absolute_uri(
            request,
            url)
        return ret

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        """
        Override default method and add logo url to variables
        https://github.com/pennersr/django-allauth/blob/0.34.0/allauth/account/adapter.py#L430
        """
        current_site = get_current_site(request)
        activate_url = self.get_email_confirmation_url(
            request,
            emailconfirmation)
        ctx = {
            "user": emailconfirmation.email_address.user,
            "activate_url": activate_url,
            "current_site": current_site,
            "key": emailconfirmation.key,
            'or_logo_secondary': settings.OR_LOGO_SECONDARY,
        }
        if signup:
            email_template = 'account/email/email_confirmation_signup'
        else:
            email_template = 'account/email/email_confirmation'
        self.send_mail(email_template,
                       emailconfirmation.email_address.email,
                       ctx)
