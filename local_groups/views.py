from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from allauth.account.views import ConfirmEmailView, EmailView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.views.generic import FormView, UpdateView
from .forms import GroupManageForm, SlackInviteForm
from .models import Group
from organizing_hub.mixins import LocalGroupPermissionRequiredMixin
import os
import requests
import logging

logger = logging.getLogger(__name__)


# View for Admin updates to Group Info
class GroupManageView(
    LocalGroupPermissionRequiredMixin,
    SuccessMessageMixin,
    UpdateView
):
    model = Group
    form_class = GroupManageForm
    success_message = "Your group has been updated successfully."
    template_name_suffix = '_manage_form'
    permission_required = 'local_groups.change_group'

    def get_local_group(self):
        return self.get_object()

    # Redirect to same page on success
    def get_success_url(self):
        return reverse_lazy('groups-manage', kwargs={'slug': self.object.slug})


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


class VerifyEmailConfirmView(ConfirmEmailView):
    template_name = "verify_email_confirm.html"


class VerifyEmailRequestView(LoginRequiredMixin, EmailView):
    template_name = "verify_email_request.html"
    success_url = reverse_lazy('organizing-hub-verify-email-request')

    # Send email confirmation message on post
    def post(self, request, *args, **kwargs):
        return self._action_send(request)

    # Get email address from user model and send email confirmation
    def _action_send(self, request, *args, **kwargs):
        email = request.user.email

        try:
            email_address = EmailAddress.objects.get(
                user=request.user,
                email=email,
            )
            get_adapter(request).add_message(
                request,
                messages.INFO,
                'account/messages/'
                'email_confirmation_sent.txt',
                {'email': email})
            email_address.send_confirmation(request)
            return HttpResponseRedirect(self.get_success_url())
        except EmailAddress.DoesNotExist:
            messages.error(
                self.request,
                '''
                We are unable to verify this email address. Please try again or
                use a different email address for email verification.
                '''
            )
            return redirect('organizing-hub-verify-email-request')
