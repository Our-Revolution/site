from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from allauth.account.views import ConfirmEmailView, EmailView
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.views.generic import CreateView, FormView, TemplateView, UpdateView
from bsd.models import BSDProfile
from .decorators import verified_email_required
from .forms import EventForm, GroupManageForm, SlackInviteForm
from .models import Event, Group
import datetime
import os
import requests
import logging


logger = logging.getLogger(__name__)


@method_decorator(verified_email_required, name='dispatch')
class EventCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Event
    form_class = EventForm
    success_message = '''
    Your event was created successfully. Visit Manage & Promote Events tool
    below to view or promote your events.
    '''

    # Check if user is a group leader and has a valid bsd cons_id
    def can_access(self):
        is_group_leader = Group.objects.filter(
            rep_email__iexact=self.request.user.email,
            status__exact='approved',
        ).first() is not None
        has_valid_cons_id = self.request.user.bsdprofile.cons_id is not BSDProfile.cons_id_default
        return is_group_leader and has_valid_cons_id

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        # Set cons_id based on current user
        form.instance.creator_cons_id = self.request.user.bsdprofile.cons_id
        try:
            return super(EventCreateView, self).form_valid(form)
        except ValidationError:
            messages.error(
                self.request,
                '''
                There was an error creating your event. Please make sure all
                fields are filled with valid data and try again.
                '''
            )
            return redirect('groups-event-create')

    def get_context_data(self, **kwargs):
        context = super(EventCreateView, self).get_context_data(**kwargs)
        # Case insensitive check for group rep email matches user email
        context['group'] = Group.objects.filter(
            rep_email__iexact=self.request.user.email
        ).first()
        return context

    def get_initial(self, *args, **kwargs):
        initial = {
            'start_day': datetime.date.today() + datetime.timedelta(days=4),
            'start_time': datetime.time(hour=17, minute=0, second=0),
            'host_receive_rsvp_emails': 1,
            'public_phone': 1,
        }
        return initial

    def get_success_url(self):
        return reverse_lazy('groups-dashboard')

    # Redirect user to dashboard page
    def redirect_user(self):
        messages.error(
            self.request,
            "Please login with a Group Leader account to access this page."
        )
        return redirect('groups-dashboard')

    # Use default get logic but add custom access check
    def get(self, request, *args, **kwargs):
        if self.can_access():
            return super(EventCreateView, self).get(request, *args, **kwargs)
        else:
            return self.redirect_user()

    # Use default post logic but add custom access check
    def post(self, request, *args, **kwargs):
        if self.can_access():
            return super(EventCreateView, self).post(request, *args, **kwargs)
        else:
            return self.redirect_user()


class GroupDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "group_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super(GroupDashboardView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # Case insensitive check for group rep email matches user email
            context['group'] = Group.objects.filter(
                rep_email__iexact=self.request.user.email
            ).first()
        return context


# View for Admin updates to Group Info
@method_decorator(verified_email_required, name='dispatch')
class GroupManageView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Group
    form_class = GroupManageForm
    success_message = "Your group has been updated successfully."
    template_name_suffix = '_manage_form'

    # Redirect to same page on success
    def get_success_url(self):
        return reverse_lazy('groups-manage', kwargs={'slug': self.object.slug})

    # Check if user email is same as group leader email (case insensitive)
    def can_access(self):
        email1 = self.get_object().rep_email
        email2 = self.request.user.email
        return email1.lower() == email2.lower()

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
            return super(GroupManageView, self).get(request, *args, **kwargs)
        else:
            return self.redirect_user()

    # Use default post logic but add custom access check
    def post(self, request, *args, **kwargs):
        if self.can_access():
            return super(GroupManageView, self).post(request, *args, **kwargs)
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


class VerifyEmailConfirmView(ConfirmEmailView):
    template_name = "verify_email_confirm.html"


class VerifyEmailRequestView(LoginRequiredMixin, EmailView):
    template_name = "verify_email_request.html"
    success_url = reverse_lazy('groups-verify-email-request')

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
            pass
