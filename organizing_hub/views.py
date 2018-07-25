from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.template import Context, Template
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, FormView, TemplateView, UpdateView
from django.views.generic.base import RedirectView
from bsd.api import BSD
from bsd.forms import BSDEventForm
from bsd.models import BSDEvent, BSDProfile, duration_type_hours
from events.forms import EventPromotionForm
from events.models import EventPromotion
from local_groups.models import (
    find_local_group_by_user,
    Group as LocalGroup,
    LocalGroupAffiliation,
    LocalGroupProfile
)
from .decorators import verified_email_required
from .forms import (
    AccountCreateForm,
    GroupAdminsForm,
    PasswordChangeForm,
    PasswordResetForm,
)
from .mixins import LocalGroupPermissionRequiredMixin
from organizing_hub.tasks import lebowski
import datetime
import json
import logging
from xml.etree.ElementTree import ElementTree
from StringIO import StringIO

logger = logging.getLogger(__name__)

"""Get BSD api"""
bsd_api = BSD().api

BSD_BASE_URL = settings.BSD_BASE_URL

event_promote_admin_message_template = Template("""Hi --

One of your neighbors is hosting an organizing event in your area that you might be interested in -- are you able to attend?

Learn more and RSVP here: {{ event_url }}

You can read a message from the organizer below.

Thanks!

Our Revolution

-------------------------------------

""")
event_promote_footer_template = Template("""

----
Paid for by Our Revolution
(not the billionaires)

PO BOX 66208 - WASHINGTON, DC 20035

Email is one of the most important tools we have to reach supporters like you, but if you'd like to, click here to unsubscribe: {{ bsd_base_url }}/page/unsubscribe/
""")
EVENTS_CAPACITY_RATIO = settings.EVENTS_CAPACITY_RATIO
EVENTS_DEFAULT_SUBJECT = settings.EVENTS_DEFAULT_SUBJECT
EVENTS_PROMOTE_MAX = settings.EVENTS_PROMOTE_MAX

LOCAL_GROUPS_ROLE_GROUP_ADMIN_ID = settings.LOCAL_GROUPS_ROLE_GROUP_ADMIN_ID
ORGANIZING_HUB_DASHBOARD_URL = settings.ORGANIZING_HUB_DASHBOARD_URL
ORGANIZING_HUB_PROMOTE_ENABLED = settings.ORGANIZING_HUB_PROMOTE_ENABLED


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

    """Add Group Role to Affiliation"""
    local_group_affiliation.local_group_roles.add(local_group_role_id)


def get_event_from_bsd(event_id_obfuscated):

    '''
    Get Event from BSD
    https://github.com/bluestatedigital/bsd-api-python#raw-api-method
    '''
    api_call = '/event/get_event_details'
    api_params = {}
    request_type = bsd_api.POST
    query = {
        'event_id_obfuscated': event_id_obfuscated,
    }
    body = {
        'event_api_version': '2',
        'values': json.dumps(query)
    }

    api_result = bsd_api.doRequest(
        api_call,
        api_params,
        request_type,
        body
    )
    event_json = json.loads(api_result.body)
    event = BSDEvent.objects.from_json(event_json)

    return event


def is_event_owner(user, event):
    """Check if user cons_id matches event cons_id"""

    if hasattr(user, 'bsdprofile'):
        bsd_profile = user.bsdprofile
        cons_id = bsd_profile.cons_id
        has_valid_cons_id = cons_id != BSDProfile.cons_id_default
        if has_valid_cons_id:
            is_creator = cons_id == event.creator_cons_id
            return is_creator

    return False


def remove_local_group_role_for_user(user, local_group, local_group_role_id):
    """Remove Role for Local Group & User if it exists"""

    if hasattr(user, 'localgroupprofile'):
        local_group_profile = user.localgroupprofile
        local_group_affiliation = local_group_profile.get_affiliation_for_local_group(
            local_group
        )
        if local_group_affiliation:
            local_group_affiliation.local_group_roles.remove(
                local_group_role_id
            )


class AccountCreateView(SuccessMessageMixin, FormView):
    form_class = AccountCreateForm
    # success_message = "Your password has been updated successfully."
    # success_url = ORGANIZING_HUB_DASHBOARD_URL
    template_name = "account_create.html"

    def create_account(self, form):
        """Create account in BSD"""
        email_address = form.cleaned_data['email_address']
        password = form.cleaned_data['new_password1']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        postal_code = form.cleaned_data['postal_code']
        api_result = bsd_api.account_createAccount(
            email_address,
            password,
            first_name,
            last_name,
            postal_code
        )
        '''
        Should get 204 response on success_url???

        https://cshift.cp.bsd.net/page/api/doc#-----------------set_password-------------
        '''
        assert api_result.http_status is 204

    def form_valid(self, form):

        """Create account"""
        try:
            self.create_account(form)
        except AssertionError:
            messages.error(
                self.request,
                '''
                There was an error creating your account. Please make sure all
                fields are filled with valid data and try again.
                '''
            )
            return redirect('groups-password-change')

        return super(AccountCreateView, self).form_valid(form)


@method_decorator(verified_email_required, name='dispatch')
class EventCreateView(SuccessMessageMixin, CreateView):
    form_class = BSDEventForm
    model = BSDEvent
    success_message = '''
    Your event was created successfully. Visit Promote Events tool to promote
    your events.
    ''' if settings.EVENT_AUTO_APPROVAL else '''
    Your event was created successfully and is now being reviewed by our team.
    '''
    template_name = "event_create.html"

    def get_local_group(self):
        return find_local_group_by_user(self.request.user)

    # Check if user has a valid bsd cons_id
    def can_access(self):
        user = self.request.user
        has_valid_cons_id = hasattr(user, 'bsdprofile') and (
            user.bsdprofile.cons_id != BSDProfile.cons_id_default
        )
        return has_valid_cons_id

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
            return redirect('organizing-hub-event-create')

    def get_initial(self, *args, **kwargs):
        """Set default duration to 1 hour"""
        duration_count = 1
        duration_type = duration_type_hours

        initial = {
            'capacity': 0,
            'duration_count': duration_count,
            'duration_type': duration_type,
            'start_day': datetime.date.today() + datetime.timedelta(days=4),
            'start_time': datetime.time(hour=17, minute=0, second=0),
            'host_receive_rsvp_emails': 1,
            'public_phone': 1,
        }
        return initial

    def get_success_url(self):
        return reverse_lazy('organizing-hub-event-list')

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
        return redirect(ORGANIZING_HUB_DASHBOARD_URL)

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


class EventListView(LoginRequiredMixin, TemplateView):
    template_name = "event_list.html"

    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)

        """Get BSD Events for this User"""
        user = self.request.user
        has_valid_cons_id = hasattr(user, 'bsdprofile') and (
            user.bsdprofile.cons_id != BSDProfile.cons_id_default
        )
        if has_valid_cons_id:
            '''
            Call BSD API
            https://github.com/bluestatedigital/bsd-api-python#raw-api-method
            '''
            api_call = '/event/get_events_for_cons'
            api_params = {}
            request_type = bsd_api.POST
            query = {
                'cons_id': user.bsdprofile.cons_id,
            }
            body = {
                'event_api_version': '2',
                'values': json.dumps(query)
            }

            api_result = bsd_api.doRequest(
                api_call,
                api_params,
                request_type,
                body
            )

            try:
                """Parse and validate response"""
                assert api_result.http_status is 200
                events_json = json.loads(api_result.body)
                past_events = [BSDEvent.objects.from_json(
                    x
                ) for x in events_json["past_create_events"]]
                upcoming_events = [BSDEvent.objects.from_json(
                    x
                ) for x in events_json["up_create_events"]]
                context['past_events'] = sorted(
                    past_events,
                    key=lambda x: x.start_day,
                    reverse=True,
                )
                context['upcoming_events'] = sorted(
                    upcoming_events,
                    key=lambda x: x.start_day,
                )

                """Check if we should show event promote link"""
                context['show_event_promote_link'] = self.show_event_promote()

            except AssertionError:
                messages.error(
                    self.request,
                    "Events retrieval failed. Reload page to try again."
                )

        return context

    def show_event_promote(self):

        """Check feature flag and local group permissions"""
        if not ORGANIZING_HUB_PROMOTE_ENABLED:
            return False

        """TODO: make a template tag for local group perms?"""
        user = self.request.user
        local_group = find_local_group_by_user(user)
        permission = 'events.add_eventpromotion'

        if local_group is None:
            return False
        elif local_group.status != 'approved':
            return False
        elif not hasattr(user, 'localgroupprofile'):
            return False
        else:
            profile = user.localgroupprofile
            has_permission = profile.has_permission_for_local_group(
                local_group,
                permission
            )
            return has_permission


class EventPromoteView(
    LocalGroupPermissionRequiredMixin,
    SuccessMessageMixin,
    CreateView
):
    event = None
    form_class = EventPromotionForm
    model = EventPromotion
    permission_required = 'events.add_eventpromotion'
    success_message = '''
    Your event promotion request has been submitted and will be reviewed by our
    team.
    '''
    template_name = "event_promote.html"

    def can_access(self):
        event = self.get_event()
        user = self.request.user
        is_owner = is_event_owner(user, event)
        return is_owner

    def get_context_data(self, **kwargs):
        context = super(EventPromoteView, self).get_context_data(
            **kwargs
        )
        context['event_id_obfuscated'] = self.kwargs['event_id_obfuscated']
        return context

    def get_initial(self, *args, **kwargs):
        event = self.get_event()
        max_recipients = EVENTS_PROMOTE_MAX if event.capacity == 0 else min(
            EVENTS_PROMOTE_MAX,
            event.capacity * EVENTS_CAPACITY_RATIO
        )
        message = Template("""Hello --

We are hosting an event near you, {{ event_name }}! Can you make it? We're almost across the finish line and we need to keep up the momentum.

{{ event_url }}

Thanks!""").render(Context({
            'event_name': event.name,
            'event_url': event.absolute_url
        }))
        initial = {
            'max_recipients': max_recipients,
            'message': message,
            'subject': EVENTS_DEFAULT_SUBJECT,
        }
        return initial

    def get_local_group(self):
        return find_local_group_by_user(self.request.user)

    def form_valid(self, form):
        """If the form is valid, save the associated model."""

        """Set event external id & event name"""
        event = self.get_event()
        form.instance.event_external_id = event.event_id_obfuscated
        form.instance.event_name = event.name

        """Set user external id"""
        form.instance.user_external_id = self.request.user.bsdprofile.cons_id

        """Set cap on recipients"""
        form.instance.max_recipients = min(
            EVENTS_PROMOTE_MAX,
            form.cleaned_data['max_recipients']
        )

        """Set message header/footer content"""
        user_message = form.cleaned_data['message']
        form.instance.message = event_promote_admin_message_template.render(
            Context({
                'event_url': event.absolute_url,
            })) + user_message + event_promote_footer_template.render(Context({
                'bsd_base_url': BSD_BASE_URL,
            }))

        # Call save via super form_valid and handle BSD errors
        try:
            return super(EventPromoteView, self).form_valid(form)
        except ValidationError:
            messages.error(
                self.request,
                '''
                There was an error submitting your request. Please make sure
                all fields are filled with valid data and try again.
                '''
            )
            return redirect(
                'organizing-hub-event-promote',
                self.kwargs['event_id_obfuscated']
            )

    def get_event(self):

        if self.event is not None:
            return self.event

        event = get_event_from_bsd(self.kwargs['event_id_obfuscated'])
        self.event = event

        return self.event

    def get_success_url(self):
        return reverse_lazy('organizing-hub-event-list')

    # Use default get logic but add custom access check
    def get(self, request, *args, **kwargs):
        if self.can_access():
            return super(EventPromoteView, self).get(request, *args, **kwargs)
        else:
            raise Http404

    # Use default post logic but add custom access check
    def post(self, request, *args, **kwargs):
        if self.can_access():
            return super(EventPromoteView, self).post(request, *args, **kwargs)
        else:
            raise Http404


@method_decorator(verified_email_required, name='dispatch')
class EventUpdateView(SuccessMessageMixin, UpdateView):
    form_class = BSDEventForm
    model = BSDEvent
    object = None
    success_message = 'Your event was updated successfully.'
    template_name = "event_update.html"

    """Check if user cons_id matches event cons_id"""
    def can_access(self):
        event = self.object
        user = self.request.user
        is_owner = is_event_owner(user, event)
        return is_owner

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        # Set cons_id based on current user
        form.instance.creator_cons_id = self.request.user.bsdprofile.cons_id
        form.instance.event_id_obfuscated = self.object.event_id_obfuscated

        # Call save via super form_valid and handle BSD errors
        try:
            return super(EventUpdateView, self).form_valid(form)
        except ValidationError:
            messages.error(
                self.request,
                '''
                There was an error updating your event. Please make sure all
                fields are filled with valid data and try again.
                '''
            )
            return redirect(
                'organizing-hub-event-update',
                self.object.event_id_obfuscated
            )

    def get_local_group(self):
        return find_local_group_by_user(self.request.user)

    def get_object(self):

        if self.object is not None:
            return self.object

        event = get_event_from_bsd(self.kwargs['event_id_obfuscated'])
        self.object = event

        return self.object

    def get_success_url(self):
        return reverse_lazy('organizing-hub-event-list')

    # Use default get logic but add custom access check
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.can_access():
            return super(EventUpdateView, self).get(request, *args, **kwargs)
        else:
            raise Http404

    # Use default post logic but add custom access check
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.can_access():
            return super(EventUpdateView, self).post(request, *args, **kwargs)
        else:
            raise Http404


class GroupAdminsView(
    LocalGroupPermissionRequiredMixin,
    SuccessMessageMixin,
    FormView
):
    form_class = GroupAdminsForm
    model = LocalGroup
    permission_required = 'local_groups.add_localgroupaffiliation'
    success_message = "The group admins have been updated successfully."
    template_name = "group_admins.html"

    def form_valid(self, form):
        email = form.cleaned_data['email']
        is_admin = form.cleaned_data['is_admin']
        local_group = self.get_local_group()

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            user = None

        if is_admin:
            """Create User if it doesn't exist and add Role"""
            if not user:
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=None
                )
                """Create BSD Profile so user can use BSD login"""
                BSDProfile.objects.create(user=user)
            add_local_group_role_for_user(
                user,
                local_group,
                LOCAL_GROUPS_ROLE_GROUP_ADMIN_ID
            )
        elif user and not is_admin:
            """Remove Role for User if it exists"""
            remove_local_group_role_for_user(
                user,
                local_group,
                LOCAL_GROUPS_ROLE_GROUP_ADMIN_ID
            )

        return super(GroupAdminsView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(GroupAdminsView, self).get_context_data(
            **kwargs
        )
        """Get Local Group and current Group Admins"""
        local_group = self.get_local_group()
        group_admin_affiliations = LocalGroupAffiliation.objects.filter(
            local_group=local_group,
            local_group_roles=LOCAL_GROUPS_ROLE_GROUP_ADMIN_ID
        ).order_by('local_group_profile__user__email')
        context['group_admin_affiliations'] = group_admin_affiliations
        context['local_group'] = local_group
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


class PasswordChangeView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    FormView
):
    form_class = PasswordChangeForm
    success_message = "Your password has been updated successfully."
    success_url = ORGANIZING_HUB_DASHBOARD_URL
    template_name = "password_change.html"

    def check_old_password(self, form):
        """Check if old password is valid in BSD"""
        username = self.request.user.email
        old_password = form.cleaned_data['old_password']
        checkCredentialsResult = bsd_api.account_checkCredentials(
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
        setPasswordResult = bsd_api.account_setPassword(
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

        return super(PasswordChangeView, self).form_valid(form)


class PasswordResetView(SuccessMessageMixin, FormView):
    form_class = PasswordResetForm
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
            setPasswordResult = bsd_api.account_setPassword(
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

        return super(PasswordResetView, self).form_valid(form)

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


"""TODO: remove TaskTestView after done testing"""


class TaskTestView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        """test task"""
        logger.debug('start test')
        test = lebowski.delay(11, 22)
        logger.debug('test: ' + str(test))
        return ORGANIZING_HUB_DASHBOARD_URL
