# from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.http import HttpResponseRedirect
# from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms import GroupLeaderSyncForm
# from .models import Application
import logging

logger = logging.getLogger(__name__)


class GroupLeaderSyncView(PermissionRequiredMixin, FormView):
    """Sync all Users to update their Group Leader affiliations"""

    '''
    TODO: need to set request.current_app to self.admin_site.name?
    https://docs.djangoproject.com/en/1.10/ref/contrib/admin/#adding-views-to-admin-sites
    '''
    form_class = GroupLeaderSyncForm
    # login_url = reverse_lazy('admin:nominations_application_changelist')
    permission_required = 'local_groups.add_localgroupaffiliation'
    success_url = reverse_lazy(
        'local_groups:local_groups_localgroupaffiliation_changelist'
    )
    template_name = 'admin/group_leader_sync.html'

    def form_valid(self, form):
        """Trigger post-save signal for all users to sync group leader roles"""
        users = User.objects.all()
        for user in users:
            post_save.send(User, instance=user)

        return HttpResponseRedirect(self.get_success_url())
