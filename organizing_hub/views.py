from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, FormView
# from django.views.generic import CreateView, FormView, UpdateView
from django.views.generic.list import ListView
from bsd.api import BSD
from bsd.forms import BSDEventForm
from bsd.models import BSDEvent, BSDProfile
from local_groups.models import (
    Group as LocalGroup,
    LocalGroupAffiliation,
    LocalGroupProfile
)
from .forms import GroupAdminsForm
from .mixins import LocalGroupPermissionRequiredMixin
import datetime
import logging


logger = logging.getLogger(__name__)

"""Get BSD api"""
bsdApi = BSD().api

LOCAL_GROUPS_ROLE_GROUP_ADMIN_ID = settings.LOCAL_GROUPS_ROLE_GROUP_ADMIN_ID


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


class EventCreateView(
    LocalGroupPermissionRequiredMixin,
    SuccessMessageMixin,
    CreateView
):
    model = BSDEvent
    form_class = BSDEventForm
    success_message = '''
    Your event was created successfully. Visit Manage & Promote Events tool
    below to view or promote your events.
    ''' if settings.EVENT_AUTO_APPROVAL else '''
    Your event was created successfully and is now being reviewed by our team.
    '''
    permission_required = 'local_groups.add_event'

    def get_local_group(self):
        local_group = None
        user = self.request.user

        if hasattr(user, 'localgroupprofile'):
            local_group_profile = user.localgroupprofile

            # TODO: support multiple group affiliations?
            local_group_affiliation = LocalGroupAffiliation.objects.filter(
                local_group_profile=local_group_profile,
                local_group__status__exact='approved',
            ).first()
            if local_group_affiliation:
                local_group = local_group_affiliation.local_group

        return local_group

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


class EventListView(ListView):

    model = BSDEvent

    def get_queryset(self):
        """
        Return the list of items for this view.
        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """

        """Return list if we already have it"""
        if self.queryset is not None:
            return self.queryset

        '''
        Save event to BSD
        https://github.com/bluestatedigital/bsd-api-python#raw-api-method
        '''
        api_call = '/event/create_event'
        api_params = {}
        request_type = bsdApi.POST
        query = {
            # Show Attendee First Names + Last Initial
            'attendee_visibility': 'FIRST',
            'capacity': self.capacity,
            'contact_phone': self.contact_phone,
            'creator_cons_id': self.creator_cons_id,
            'creator_name': self.host_name,
            'event_type_id': self.event_type,
            'days': [{
                'start_datetime_system': str(datetime.datetime.combine(
                    self.start_day,
                    self.start_time
                )),
                'duration': self.duration_minutes()
            }],
            'description': self.description,
            'flag_approval': flag_approval,
            'host_receive_rsvp_emails': self.host_receive_rsvp_emails,
            'local_timezone': self.start_time_zone,
            'name': self.name,
            'public_phone': self.public_phone,
            'venue_addr1': self.venue_addr1,
            'venue_addr2': self.venue_addr2,
            'venue_city': self.venue_city,
            'venue_directions': self.venue_directions,
            'venue_name': self.venue_name,
            'venue_state_cd': self.venue_state_or_territory,
            'venue_zip': self.venue_zip,
        }
        body = {
            'event_api_version': '2',
            'values': json.dumps(query)
        }

        apiResult = bsdApi.doRequest(api_call, api_params, request_type, body)

        try:
            # Parse and validate response
            assert apiResult.http_status is 200
            assert 'event_id_obfuscated' in json.loads(apiResult.body)
        except AssertionError:
            raise ValidationError('''
                Event creation failed, please check data and try again.
            ''')


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
