from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from calls.models import (
    CallCampaign,
    CallCampaignStatus,
    find_campaigns_as_caller,
    find_campaigns_as_admin,
    call_campaign_statuses_active
)
import logging

logger = logging.getLogger(__name__)


class CallDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "call/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super(CallDashboardView, self).get_context_data(**kwargs)

        """Find campaigns as admin or caller"""
        user = self.request.user
        if hasattr(user, 'callprofile'):
            call_profile = user.callprofile
            campaigns_as_admin = find_campaigns_as_admin(call_profile)
            campaigns_as_admin_sorted = sorted(
                campaigns_as_admin,
                key=lambda x: x.is_in_progress,
                reverse=True,
            )
            campaigns_as_admin_active = [
                x for x in campaigns_as_admin_sorted if x.is_active
            ]
            campaigns_as_admin_inactive = [
                x for x in campaigns_as_admin_sorted if not x.is_active
            ]
            campaigns_as_caller = find_campaigns_as_caller(call_profile)
            campaigns_as_caller_sorted = sorted(
                campaigns_as_caller,
                key=lambda x: x.is_in_progress,
                reverse=True,
            )
            campaigns_as_caller_active = [
                x for x in campaigns_as_caller_sorted if x.is_active
            ]

            context['campaigns_as_admin_active'] = campaigns_as_admin_active
            context['campaigns_as_admin_inactive'] = campaigns_as_admin_inactive
            context['campaigns_as_caller_active'] = campaigns_as_caller_active

        return context
