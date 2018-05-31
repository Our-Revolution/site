from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from allauth.account.views import ConfirmEmailView, EmailView
from django.conf import settings
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views.generic import CreateView, FormView, UpdateView
from StringIO import StringIO
from xml.etree.ElementTree import ElementTree
from bsd.api import BSD
from bsd.models import BSDProfile
from organizing_hub.decorators import verified_email_required
from organizing_hub.mixins import LocalGroupPermissionRequiredMixin
from .forms import (
    EventForm,
    GroupManageForm,
    GroupPasswordChangeForm,
    GroupPasswordResetForm,
    SlackInviteForm,
)
from .models import Event, Group
import datetime
import os
import requests
import logging

# Get bsd api
bsdApi = BSD().api

logger = logging.getLogger(__name__)


@method_decorator(verified_email_required, name='dispatch')
class EventCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Event
    form_class = EventForm
    success_message = '''
    Your event was created successfully. Visit Manage & Promote Events tool
    below to view or promote your events.
    ''' if settings.EVENT_AUTO_APPROVAL else '''
    Your event was created successfully and is now being reviewed by our team.
    '''

    # Check if user is a group leader and has a valid bsd cons_id
    def can_access(self):
        is_group_leader = Group.objects.filter(
            rep_email__iexact=self.request.user.email,
            status__exact='approved',
        ).first() is not None
        user = self.request.user
        has_valid_cons_id = hasattr(user, 'bsdprofile') and (
            user.bsdprofile.cons_id != BSDProfile.cons_id_default
        )
        return is_group_leader and has_valid_cons_id

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        # Set cons_id based on current user
        form.instance.creator_cons_id = self.request.user.bsdprofile.cons_id

        # Call save via super form_valid and handle BSD errors
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

    def get_initial(self, *args, **kwargs):
        initial = {
            'start_day': datetime.date.today() + datetime.timedelta(days=4),
            'start_time': datetime.time(hour=17, minute=0, second=0),
            'host_receive_rsvp_emails': 1,
            'public_phone': 1,
        }
        return initial

    def get_success_url(self):
        return settings.ORGANIZING_HUB_DASHBOARD_URL

    # Redirect user to dashboard page
    def redirect_user(self):
        messages.error(
            self.request,
            '''
            This is not a Group Leader account, or your session is out of date.
            Please logout and log back in with a Group Leader account to access
            this page.
            '''
        )
        return redirect(settings.ORGANIZING_HUB_DASHBOARD_URL)

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
    # local_group = object
    # form_class = ApplicationsStatusChangeForm
    # login_url = reverse_lazy('admin:nominations_application_changelist')
    permission_required = 'local_groups.change_group'
    # success_url = reverse_lazy('admin:nominations_application_changelist')
    # template_name = 'admin/applications_status_change.html'

    def get_local_group(self):
        """
        Override this method to override the local_group attribute.
        """
        return self.get_object()

    # Redirect to same page on success
    def get_success_url(self):
        return reverse_lazy('groups-manage', kwargs={'slug': self.object.slug})

    # Check if user email is same as group leader email (case insensitive)
    # def can_access(self):
    #     email1 = self.get_object().rep_email
    #     email2 = self.request.user.email
    #     return email1.lower() == email2.lower()

    # Redirect user to dashboard page
    # def redirect_user(self):
    #     messages.error(
    #         self.request,
    #         "Please login with the Group Leader account to access this page."
    #     )
    #     return redirect(settings.ORGANIZING_HUB_DASHBOARD_URL)

    # Use default get logic but add custom access check
    # def get(self, request, *args, **kwargs):
    #     if self.can_access():
    #         return super(GroupManageView, self).get(request, *args, **kwargs)
    #     else:
    #         return self.redirect_user()

    # Use default post logic but add custom access check
    # def post(self, request, *args, **kwargs):
    #     if self.can_access():
    #         return super(GroupManageView, self).post(request, *args, **kwargs)
    #     else:
    #         return self.redirect_user()


class GroupPasswordChangeView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    FormView
):
    form_class = GroupPasswordChangeForm
    success_message = "Your password has been updated successfully."
    success_url = settings.ORGANIZING_HUB_DASHBOARD_URL
    template_name = "password_change.html"

    def check_old_password(self, form):
        """Check if old password is valid in BSD"""
        username = self.request.user.email
        old_password = form.cleaned_data['old_password']
        checkCredentialsResult = bsdApi.account_checkCredentials(
            username,
            old_password
        )

        '''
        Should get 200 response and constituent record

        https://cshift.cp.bsd.net/page/api/doc#---------------------check_credentials-----------------
        '''
        assert checkCredentialsResult.http_status is 200
        tree = ElementTree().parse(StringIO(checkCredentialsResult.body))
        cons = tree.find('cons')
        assert cons is not None
        cons_id = cons.get('id')
        assert cons_id is not None
        assert cons.find('has_account').text == "1"
        assert cons.find('is_banned').text == "0"

    def set_new_password(self, form):
        """Set new password in BSD"""
        username = self.request.user.email
        new_password = form.cleaned_data['new_password1']
        setPasswordResult = bsdApi.account_setPassword(
            username,
            new_password
        )
        '''
        Should get 204 response on success_url

        https://cshift.cp.bsd.net/page/api/doc#-----------------set_password-------------
        '''
        assert setPasswordResult.http_status is 204

    def form_valid(self, form):
        """Check old password"""
        try:
            self.check_old_password(form)
        except AssertionError:
            messages.error(
                self.request,
                '''
                There was an error validating your old password. Please make
                sure all fields are filled with correct data and try again.
                '''
            )
            return redirect('groups-password-change')

        """Set new password"""
        try:
            self.set_new_password(form)
        except AssertionError:
            messages.error(
                self.request,
                '''
                There was an error setting your new password. Please make
                sure all fields are filled with correct data and try again.
                '''
            )
            return redirect('groups-password-change')

        return super(GroupPasswordChangeView, self).form_valid(form)


class GroupPasswordResetView(SuccessMessageMixin, FormView):
    form_class = GroupPasswordResetForm
    success_message = "Your password has been reset successfully."
    success_url = reverse_lazy('groups-login')
    template_name = "registration/password_reset_confirm.html"

    def form_invalid(self, form, user):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        return self.render_to_response(self.get_context_data(
            form=form,
            email=user.email
        ))

    def form_valid(self, form, user):
        try:
            """Set new password in BSD"""
            username = user.email
            new_password = form.cleaned_data['new_password1']
            setPasswordResult = bsdApi.account_setPassword(
                username,
                new_password
            )
            '''
            Should get 204 response on success_url

            https://cshift.cp.bsd.net/page/api/doc#-----------------set_password-------------
            '''
            assert setPasswordResult.http_status is 204

        except AssertionError:
            messages.error(
                self.request,
                '''
                There was an error resetting your password. Please make
                sure all fields are filled with correct data and try again.
                '''
            )
            return redirect(reverse_lazy('password_reset_confirm', kwargs={
                'token': self.kwargs['token'],
                'uidb64': self.kwargs['uidb64'],
            }))

        return super(GroupPasswordResetView, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        """Get user if url is valid"""
        user = self.get_user_from_url(request)
        if user:
            return self.render_to_response(self.get_context_data(
                email=user.email
            ))
        else:
            return self.redirect_user()

    """
    Verify that the url is valid and return user.

    Based on https://github.com/django/django/blob/stable/1.10.x/django/contrib/auth/views.py#L236
    """
    def get_user_from_url(self, request, *args, **kwargs):
        uidb64 = self.kwargs['uidb64']
        token = self.kwargs['token']

        """Check the hash in password reset link."""
        UserModel = get_user_model()
        assert uidb64 is not None and token is not None  # checked by URLconf

        try:
            # urlsafe_base64_decode() decodes to bytestring on Python 3
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None

        validlink = user is not None and default_token_generator.check_token(
            user,
            token
        )

        if validlink:
            return user
        else:
            return None

    def post(self, request, *args, **kwargs):
        """Get user if url is valid"""
        user = self.get_user_from_url(request)
        if user:
            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form, user)
            else:
                return self.form_invalid(form, user)
        else:
            return self.redirect_user()

    def redirect_user(self):
        messages.error(
            self.request,
            '''
            The password reset link was invalid, possibly because it has
            already been used.  Please request a new password reset.
            '''
        )
        return redirect('password_reset')


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
            messages.error(
                self.request,
                '''
                We are unable to verify this email address. Please try again or
                use a different email address for email verification.
                '''
            )
            return redirect('groups-verify-email-request')
