from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, TemplateView, DetailView, FormView
from django.http import HttpResponseRedirect
from .forms import ApplicationsStatusChangeForm
from .models import Application, Nomination, InitiativeApplication
import json, os
from urlparse import urlparse
from django.utils.decorators import method_decorator
from django.template.loader import get_template
from django.template import Context

from easy_pdf.views import PDFTemplateView

import logging

logger = logging.getLogger(__name__)


class ApplicationPDFView(PDFTemplateView):

    template_name = 'admin/application_pdf.html'

    def get_context_data(self, **kwargs):
        app_id = self.request.GET.get('id')
        app = get_object_or_404(
            Application.objects.select_related(),
            pk=app_id
        )

        return super(ApplicationPDFView, self).get_context_data(
            pagesize='letter',
            title=app,
            app=app,
            base_url=settings.BASE_URL,
            **kwargs
        )



class ApplicationsStatusChangeView(PermissionRequiredMixin, FormView):
    '''
    TODO: need to set request.current_app to self.admin_site.name?
    https://docs.djangoproject.com/en/1.10/ref/contrib/admin/#adding-views-to-admin-sites
    '''
    form_class = ApplicationsStatusChangeForm
    login_url = reverse_lazy('admin:nominations_application_changelist')
    permission_required = 'nominations.bulk_change_application_status'
    success_url = reverse_lazy('admin:nominations_application_changelist')
    template_name = 'admin/applications_status_change.html'

    def get_context_data(self, **kwargs):
        context = super(ApplicationsStatusChangeView, self).get_context_data(
            **kwargs
        )
        context['status'] = self.kwargs['status']
        ids = self.request.GET.getlist('id')
        context['applications'] = Application.objects.filter(pk__in=ids)
        return context

    def form_valid(self, form):
        status = self.kwargs['status']
        ids = self.request.GET.getlist('id')
        Application.objects.filter(pk__in=ids).update(status=status)
        return HttpResponseRedirect(self.get_success_url())
