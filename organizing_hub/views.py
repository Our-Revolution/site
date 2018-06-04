from django.urls import reverse_lazy
# from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import FormView
from local_groups.models import (
    Group as LocalGroup,
    LocalGroupAffiliation,
    LocalGroupProfile
)
from .forms import GroupAdminsForm
import logging


logger = logging.getLogger(__name__)


"""TODO: require permission for local group"""


def add_local_group_role_for_user(user, local_group, local_group_role_id):
    """
    Add Local Group Role to Affiliation for User & Group. Create Profile and
    Affiliation if they don't already exist
    """

    """Get or create Local Group Profile for User"""
    if hasattr(user, 'localgroupprofile'):
        local_group_profile = user.localgroupprofile
    else:
        local_group_profile = LocalGroupProfile.objects.create(
            user=user
        )

    """Get or create Local Group Affiliation for User & Group"""
    local_group_affiliation = local_group_profile.get_affiliation_for_local_group(
        local_group
    )
    if not local_group_affiliation:
        local_group_affiliation = LocalGroupAffiliation.objects.create(
            local_group=local_group,
            local_group_profile=local_group_profile
        )

    """Add Group Leader role to Affiliation if it doesn't exist"""
    if not local_group_affiliation.local_group_roles.filter(
        id=local_group_role_id
    ).exists():
        local_group_affiliation.local_group_roles.add(
            local_group_role_id
        )


class GroupAdminsView(LocalGroupPermissionRequiredMixin, FormView):
    form_class = GroupAdminsForm
    model = LocalGroup
    permission_required = 'local_groups.add_localgroupaffiliation'
    success_message = "Group Admins have been updated successfully."
    template_name = "group_admins.html"
    local_group = None

    def form_valid(self, form):
        email = form.cleaned_data['email']
        is_admin = form.cleaned_data['is_admin']
        if is_admin:
            add_role_for_user()
        else:
            remove_role_for_user()
        return super(GroupAdminsView, self).form_valid(form)

        # """Check old password"""
        # try:
        #     self.check_old_password(form)
        # except AssertionError:
        #     messages.error(
        #         self.request,
        #         '''
        #         There was an error validating your old password. Please make
        #         sure all fields are filled with correct data and try again.
        #         '''
        #     )
        #     return redirect('groups-password-change')
        #
        # """Set new password"""
        # try:
        #     self.set_new_password(form)
        # except AssertionError:
        #     messages.error(
        #         self.request,
        #         '''
        #         There was an error setting your new password. Please make
        #         sure all fields are filled with correct data and try again.
        #         '''
        #     )
        #     return redirect('groups-password-change')
        #
        # return super(GroupAdminsView, self).form_valid(form)

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
