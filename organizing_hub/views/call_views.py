# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, FormView, TemplateView
from django.views.generic.list import ListView
from calls.forms import CallForm, CallCampaignForm
from calls.models import (
    CallCampaign,
    CallCampaignStatus,
    CallProfile,
    find_campaigns_as_caller,
    find_campaigns_as_admin,
    call_campaign_statuses_active
)
from local_groups.models import find_local_group_by_user
from organizing_hub.mixins import LocalGroupPermissionRequiredMixin
import logging

logger = logging.getLogger(__name__)

CALLS_MAX_DISTANCE_MILES = settings.CALLS_MAX_DISTANCE_MILES
CALLS_MAX_LIST_SIZE = settings.CALLS_MAX_LIST_SIZE

campaign_script_template = """Hi, my name is (your name), I'm a volunteer for (your group), is (first name) available?

(After confirming that you've reached the right person)

How are you today?

(your group) is holding our monthly membership meeting on (event date) at (event location). We'll be talking about (event topic).

Would you be able to attend?
"""


class CallView(
    # LocalGroupPermissionRequiredMixin,
    # SuccessMessageMixin,
    FormView
):
    form_class = CallForm
    template_name = 'calls/call_form.html'
    # local_group = None
    # permission_required = 'calls.add_callcampaign'
    # success_message = '''
    # Your calling campaign request has been submitted and will be reviewed by
    # our team.
    # '''

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        # form.send_email()
        return super(CallView, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        return redirect('organizing-hub-call-dashboard')
    # def form_valid(self, form):
    #     """Set local group and owner before save"""
    #     form.instance.local_group = self.get_local_group()
    #     form.instance.owner = self.request.user.callprofile
    #     return super(CallCampaignCreateView, self).form_valid(form)
    #
    # def get_local_group(self):
    #     if self.local_group is None:
    #         self.local_group = find_local_group_by_user(self.request.user)
    #     return self.local_group
    #
    # def get_initial(self, *args, **kwargs):
    #     initial = {
    #         'max_distance': min(25, CALLS_MAX_DISTANCE_MILES),
    #         'max_recipients': min(100, CALLS_MAX_LIST_SIZE),
    #         'script': campaign_script_template,
    #     }
    #     return initial
    #
    # def get_success_url(self):
    #     return reverse_lazy(
    #         'organizing-hub-call-campaign-detail',
    #         kwargs={'uuid': self.object.uuid}
    #     )


class CallCampaignCreateView(
    LocalGroupPermissionRequiredMixin,
    SuccessMessageMixin,
    CreateView
):
    form_class = CallCampaignForm
    local_group = None
    model = CallCampaign
    permission_required = 'calls.add_callcampaign'
    success_message = '''
    Your calling campaign request has been submitted and will be reviewed by
    our team.
    '''

    def form_valid(self, form):
        """Set local group and owner before save"""
        form.instance.local_group = self.get_local_group()
        form.instance.owner = self.request.user.callprofile
        return super(CallCampaignCreateView, self).form_valid(form)

    def get_local_group(self):
        if self.local_group is None:
            self.local_group = find_local_group_by_user(self.request.user)
        return self.local_group

    def get_initial(self, *args, **kwargs):
        initial = {
            'max_distance': min(25, CALLS_MAX_DISTANCE_MILES),
            'max_recipients': min(100, CALLS_MAX_LIST_SIZE),
            'script': campaign_script_template,
        }
        return initial

    def get_success_url(self):
        return reverse_lazy(
            'organizing-hub-call-campaign-detail',
            kwargs={'uuid': self.object.uuid}
        )


class CallCampaignDetailView(LocalGroupPermissionRequiredMixin, DetailView):
    context_object_name = 'campaign'
    model = CallCampaign
    permission_required = 'calls.change_callcampaign'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_local_group(self):
        return find_local_group_by_user(self.request.user)


class CallDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "calls/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super(CallDashboardView, self).get_context_data(**kwargs)

        """Find campaigns as admin or caller"""
        user = self.request.user
        if hasattr(user, 'callprofile'):
            call_profile = user.callprofile
        else:
            """Create call profile if doesn't exist"""
            call_profile = CallProfile.objects.create(user=user)

        campaigns_as_admin = find_campaigns_as_admin(call_profile)
        campaigns_as_admin_sorted = sorted(
            campaigns_as_admin,
            key=lambda x: x.is_in_progress,
            reverse=True,
        )
        campaigns_as_admin_active = [(
            x,
            CallForm() if x.is_in_progress else None
        ) for x in campaigns_as_admin_sorted if x.is_active]
        campaigns_as_admin_inactive = [
            (x, None) for x in campaigns_as_admin_sorted if not x.is_active
        ]
        campaigns_as_caller = find_campaigns_as_caller(call_profile)
        campaigns_as_caller_sorted = sorted(
            campaigns_as_caller,
            key=lambda x: x.is_in_progress,
            reverse=True,
        )
        campaigns_as_caller_active = [(
            x,
            CallForm() if x.is_in_progress else None
        ) for x in campaigns_as_caller_sorted if x.is_active]

        context['campaigns_as_admin_active'] = campaigns_as_admin_active
        context['campaigns_as_admin_inactive'] = campaigns_as_admin_inactive
        context['campaigns_as_caller_active'] = campaigns_as_caller_active

        return context
