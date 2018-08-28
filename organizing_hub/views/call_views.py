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
from local_groups.models import find_local_group_by_user
import logging

logger = logging.getLogger(__name__)


class CallDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "call/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super(CallDashboardView, self).get_context_data(**kwargs)

        user = self.request.user
        if hasattr(user, 'callprofile'):
            call_profile = user.callprofile
            campaigns_as_admin = find_campaigns_as_admin(call_profile)
            campaigns_as_caller = find_campaigns_as_caller(call_profile)
            active_status_ids = [
                x.value[0] for x in call_campaign_statuses_active
            ]
            context['campaigns_as_admin_active'] = campaigns_as_admin.filter(
                status__in=active_status_ids,
            )
            context['campaigns_as_admin_inactive'] = campaigns_as_admin.exclude(
                status__in=active_status_ids,
            )
            context['campaigns_as_caller_active'] = campaigns_as_caller.filter(
                status__in=active_status_ids,
            )
            context['campaigns_as_caller_inactive'] = campaigns_as_caller.exclude(
                status__in=active_status_ids,
            )

        # context['campaign_list'] = sorted(
        #     past_events,
        #     key=lambda x: x.start_day,
        #     reverse=True,
        # )

        return context
