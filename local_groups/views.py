from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView, UpdateView
from .forms import SlackInviteForm
from .models import Group
import os
import requests


# TODO: replace with real page
class GroupDashboardView(TemplateView):
    template_name = "group_dashboard.html"


# View for Admin updates to Group Info
class GroupUpdateView(LoginRequiredMixin, UpdateView):
    model = Group
    fields = [
        'description',
        'city',
        'state',
        'county',
        'country',
        'postal_code',
        'size',
        # Edit group email instead of rep email so BSD auth still works
        'group_contact_email',
        'rep_first_name',
        'rep_last_name',
        'rep_phone',
        'rep_postal_code',
        'website_url',
        'facebook_url',
        'twitter_url',
        'instagram_url',
        'other_social',
        'types_of_organizing',
        'other_types_of_organizing',
        'issues',
        'other_issues',
        'constituency',
        'last_meeting',
        'recurring_meeting',
        'meeting_address_line1',
        'meeting_address_line2',
        'meeting_city',
        'meeting_state_province',
        'meeting_postal_code',
        'meeting_country',
    ]
    template_name_suffix = '_update_form'

    # Redirect to same page on success
    def get_success_url(self):
        return "/groups/" + self.object.slug + "/update/"

    # Check if user email is same as group leader email
    def can_access(self):
        return self.get_object().rep_email == self.request.user.email

    # Redirect user to dashboard page
    def redirect_user(self):
        messages.error(
            self.request,
            "Please login with the Group Leader account to access this page."
        )
        return redirect('groups-dashboard')

    # Use default get logic but add custom access check
    def get(self, request, *args, **kwargs):
        if self.can_access():
            return super(GroupUpdateView, self).get(request, *args, **kwargs)
        else:
            return self.redirect_user()

    # Use default post logic but add custom access check
    def post(self, request, *args, **kwargs):
        if self.can_access():
            return super(GroupUpdateView, self).post(request, *args, **kwargs)
        else:
            return self.redirect_user()


class SlackInviteView(FormView):
    form_class = SlackInviteForm
    template_name = "slack_invite.html"
    success_url = '/'

    def form_valid(self, form):

        first_name, last_name = ["", ""]
        full_name = form.cleaned_data['full_name']

        if full_name and ' ' in full_name:
            first_name, last_name = full_name.split(' ', 1)
        elif full_name:
            first_name = full_name

        # invite to Slack

        params = ["token=%s" % os.environ['LOCAL_OR_ORGANIZING_API_TOKEN'], "email=%s" % form.cleaned_data['email']]

        if first_name:
            params.append("first_name=%s" % first_name)

        if last_name:
            params.append("last_name=%s" % last_name)

        if form.cleaned_data['state']:
            params.append("channels=%s" % form.cleaned_data['state'])

        req = requests.post('https://slack.com/api/users.admin.invite?%s' % '&'.join(params))

        messages.success(self.request, "Your Slack invitation has been sent -- check your inbox.")

        # redirect
        return super(SlackInviteView, self).form_valid(form)
