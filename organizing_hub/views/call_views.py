from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from calls.models import (
    CallCampaign,
    CallCampaignStatus,
    find_campaigns_as_caller,
    find_campaigns_as_editor
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
            context['campaigns_as_caller'] = find_campaigns_as_caller(
                call_profile
            )
            context['campaigns_as_editor'] = find_campaigns_as_editor(
                call_profile
            )

        # context['campaign_list'] = sorted(
        #     past_events,
        #     key=lambda x: x.start_day,
        #     reverse=True,
        # )

        return context
