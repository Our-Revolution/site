from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
import logging

logger = logging.getLogger(__name__)


class CallDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "call/dashboard.html"
