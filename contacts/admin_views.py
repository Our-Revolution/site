# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms import PhoneOptOutUploadForm
from .models import add_phone_opt_out, OptOutType
import csv
import logging

logger = logging.getLogger(__name__)


class PhoneOptOutUploadView(PermissionRequiredMixin, FormView):
    """
    Upload CSV of Phone Opt Outs for Calling and save any new ones to db

    Always assumes Opt Out Type = Calling. Do not upload other types.

    TODO: need to set request.current_app to self.admin_site.name?
    https://docs.djangoproject.com/en/1.11/ref/contrib/admin/#adding-views-to-admin-sites
    """

    '''
    '''
    form_class = PhoneOptOutUploadForm
    login_url = reverse_lazy(
        'admin:contacts_phoneoptout_changelist'
    )
    permission_required = 'contacts.add_phoneoptout'
    success_url = reverse_lazy(
        'admin:contacts_phoneoptout_changelist'
    )
    template_name = 'admin/phone_opt_out_upload.html'

    def form_valid(self, form):
        """Handle file upload"""
        csv_file = self.request.FILES['csv_file']
        reader = csv.DictReader(csv_file, fieldnames=['phone'])

        """Set source code"""
        user = self.request.user
        source = 'Admin Upload by %s [%s]' % (user.email, str(user.id))

        for row in reader:
            phone = row['phone']
            result = add_phone_opt_out(phone, OptOutType.calling, source)
            messages.success(
                self.request,
                "Call response saved successfully."
            )

        return HttpResponseRedirect(self.get_success_url())
