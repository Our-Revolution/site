from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms import GroupLeaderSyncForm
import logging

logger = logging.getLogger(__name__)


class PhoneOptOutUploadView(PermissionRequiredMixin, FormView):
    """Sync all Users to update their Group Leader affiliations"""

    '''
    TODO: need to set request.current_app to self.admin_site.name?
    https://docs.djangoproject.com/en/1.10/ref/contrib/admin/#adding-views-to-admin-sites
    '''
    form_class = GroupLeaderSyncForm
    login_url = reverse_lazy(
        'admin:contacts_phoneoptout_changelist'
    )
    permission_required = 'contacts.add_phoneoptout'
    success_url = reverse_lazy(
        'admin:contacts_phoneoptout_changelist'
    )
    template_name = 'admin/phone_opt_out_upload.html'

    def form_valid(self, form):
        """Trigger post-save signal for all users to sync group leader roles"""
        users = User.objects.all()
        for user in users:
            post_save.send(User, instance=user)

        return HttpResponseRedirect(self.get_success_url())
