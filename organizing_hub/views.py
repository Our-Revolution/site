from django.urls import reverse_lazy
# from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import FormView
from local_groups.models import Group as LocalGroup
from .forms import GroupAdminsForm
import logging


logger = logging.getLogger(__name__)


"""TODO: require permission for local group"""


class GroupAdminsView(FormView):
    form_class = GroupAdminsForm
    model = LocalGroup
    permission_required = 'local_groups.add_localgroupaffiliation'
    success_message = "Group Admins have been updated successfully."
    template_name = "group_admins.html"
    local_group = None

    def get_context_data(self, **kwargs):
        context = super(GroupAdminsView, self).get_context_data(
            **kwargs
        )
        """TODO: get all current Group Admins"""
        # context['slug'] = self.kwargs['slug']
        context['local_group'] = self.get_local_group()
        return context

    def get_local_group(self):
        if not self.local_group:
            self.local_group = get_object_or_404(
                LocalGroup,
                slug=self.kwargs['slug'],
                status__exact='approved',
            )
        return self.local_group

    def get_success_url(self):
        return reverse_lazy(
            'organizing-hub-group-admins',
            kwargs={'slug': self.kwargs['slug']}
        )
