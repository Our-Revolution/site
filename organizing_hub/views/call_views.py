from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView, TemplateView
from django.views.generic.list import ListView
from calls.models import (
    CallCampaign,
    CallCampaignStatus,
    find_campaigns_as_caller,
    find_campaigns_as_admin,
    call_campaign_statuses_active
)
from local_groups.models import find_local_group_by_user
from organizing_hub.forms import CallCampaignForm
from organizing_hub.mixins import LocalGroupPermissionRequiredMixin
import logging

logger = logging.getLogger(__name__)


class CallCampaignCreateView(
    LocalGroupPermissionRequiredMixin,
    SuccessMessageMixin,
    CreateView
):
    form_class = CallCampaignForm
    model = CallCampaign
    permission_required = 'calls.add_callcampaign'
    success_message = '''
    Your call campaign request has been submitted and will be reviewed by our
    team.
    '''
    # template_name = "event_promote.html"

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
