from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from calls.models import CallCampaign, CallCampaignStatus
import logging

logger = logging.getLogger(__name__)


"""Statuses for Caller display"""
call_campaign_statuses_for_caller = [
    CallCampaignStatus.approved,
    CallCampaignStatus.in_progress,
    CallCampaignStatus.paused,
    CallCampaignStatus.complete,
]


class CallDashboardView(LoginRequiredMixin, ListView):
    context_object_name = 'campaign_list'
    template_name = "call/dashboard.html"

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'callprofile'):
            queryset = CallCampaign.objects.filter(
                owner=user.callprofile,
                status__in=[x.value[0] for x in call_campaign_statuses_for_caller],
            )
        else:
            queryset = CallCampaign.objects.none()
        return queryset
