# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from bsd.models import BSDProfile
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    TemplateView,
    UpdateView,
)
from django.views.generic.list import ListView
from calls.forms import CallForm, CallCampaignForm, CallCampaignUpdateForm
from calls.models import (
    call_campaign_statuses_active,
    find_calls_made_by_campaign,
    find_or_create_active_call_for_campaign_and_caller,
    save_call_response,
    Call,
    CallAnswer,
    CallCampaign,
    CallCampaignStatus,
    CallProfile,
    CallQuestion,
)
from contacts.models import has_phone_opt_out, OptOutType
from local_groups.models import find_local_group_by_user
from organizing_hub.decorators import verified_email_required
from organizing_hub.mixins import LocalGroupPermissionRequiredMixin
from organizing_hub.models import (
    find_campaigns_as_admin,
    find_campaigns_as_caller,
    has_call_feature_access_for_local_group,
    has_call_permission_for_local_group,
    OrganizingHubFeature,
)
import logging
import unicodecsv

logger = logging.getLogger(__name__)

CALLS_MAX_DISTANCE_MILES = settings.CALLS_MAX_DISTANCE_MILES
CALLS_MAX_LIST_SIZE = settings.CALLS_MAX_LIST_SIZE

campaign_script_template = """Hi, my name is (your name), I'm a volunteer for (your group), is (first name) available?

(After confirming that you've reached the right person)

How are you today?

(your group) is holding our monthly membership meeting on (event date) at (event location). We'll be talking about (event topic).

Would you be able to attend?
"""


def can_change_call_campaign(user, call_campaign):
    """
    Check if User has change access for Call Campaign

    Parameters
    ----------
    user : User
        User to check for access
    call_campaign : CallCampaign
        Call Campaign to check for access

    Returns
        -------
        bool
            Returns True if User can change Call Campaign, otherwise False
    """

    """Check if User has change access for Campaign"""
    return has_call_permission_for_local_group(
        user,
        call_campaign.local_group,
        'calls.change_callcampaign'
    )


def can_make_call_for_campaign(user, call_campaign):
    """
    Check if User has access to make a Call for Campaign

    Should have access if Campaign is In Progress, Campaign Local Group has
    Feature Access, and User is either a Caller for Campaign or has change
    permissions for Campaign.

    Parameters
    ----------
    user : User
        User to check for access
    call_campaign : CallCampaign
        Call Campaign to check for access

    Returns
        -------
        bool
            Return True if User can Call for Campaign
    """

    """Check Campaign status"""
    if call_campaign.is_in_progress:

        """Check if User is Caller on Campaign"""
        if hasattr(user, 'callprofile') and (
            user.callprofile in call_campaign.callers.all()
        ):
            """Check if Local Group for Campaign has Call Tool Access"""
            return has_call_feature_access_for_local_group(
                call_campaign.local_group
            )
        else:
            """Check if User has change level access on Campaign"""
            return can_change_call_campaign(user, call_campaign)

    """Otherwise return False"""
    return False


def get_or_create_callers(caller_emails):
    """
    Get or create callers from a list of caller emails

    Parameters
    ----------
    emails : list of str
        List of email addresses

    Returns
        -------
        Callers list
            Returns list of ints corresponding to callprofile IDs
    """

    caller_ids = []

    if caller_emails is not None and caller_emails != '':
        """Replace spaces and linebreaks with commas"""
        caller_emails_stripped = caller_emails.replace(" ", ",").replace("\n", ",").replace("\r", ",")
        caller_emails = caller_emails_stripped.split(",")

        for email in caller_emails:
            if email is not '':
                """Get a user by email address if it exists. If we get multiple
                results, grab the first."""
                user = User.objects.filter(email__iexact=email).first()

                if not user:
                    user = User.objects.create(username=email, email=email)
                    BSDProfile.objects.create(user=user)

                """Get or create call profile which is used to store caller data"""
                (callprofile, created) = CallProfile.objects.get_or_create(
                    user=user
                )

                caller_ids.append(callprofile.id)

    return caller_ids


@method_decorator(verified_email_required, name='dispatch')
class CallView(FormView):
    """
    Call View

    Handle submit request for Make Call and also Call Responses

    TODO: separate logic for Make Call request vs Save Call request
    """

    form_class = CallForm
    template_name = 'calls/call_form.html'

    def can_access(self, call_campaign, call):
        """
        Check if current User can access View for Campaign and Call

        If Call is None then just check access for Campaign.

        Parameters
        ----------
        call_campaign : CallCampaign
            Call Campaign for checking access
        call : Call
            Call for checking access, or None

        Returns
            -------
            bool
                Return True if current User can access View
        """

        """Check if Call Campaign is not None"""
        if call_campaign is not None:

            """Check if User can make Call for Campaign"""
            user = self.request.user
            if can_make_call_for_campaign(user, call_campaign):

                """If Call is not None then check if User is Caller"""
                if call is not None:
                    return hasattr(user, 'callprofile') and (
                        call.caller == user.callprofile
                    )
                else:
                    """If Call is None then Campaign access is sufficient"""
                    return True

        """Otherwise return False"""
        return False

    def form_invalid(self, form):

        """Return Call page with new Form if there is a Call"""
        context = self.get_context_data()

        if not self.can_access(
            context['call_campaign'],
            context['call'],
        ):
            return redirect('organizing-hub-call-dashboard')

        if context['call'] is None:
            messages.info(
                self.request,
                "No more contacts left to call for this campaign."
            )
            return redirect('organizing-hub-call-dashboard')

        return self.render_to_response(context)

    def form_valid(self, form):

        """Get Call if it exists"""
        call_uuid = form.cleaned_data['call_uuid']
        call = None if call_uuid is None else Call.objects.select_related(
            'call_campaign'
        ).filter(uuid=call_uuid).first()

        """Handle Call Response"""
        if call is not None:

            if not self.can_access(
                call.call_campaign,
                call,
            ):
                return redirect('organizing-hub-call-dashboard')

            """Save Call Responses"""
            save_call_response(
                call,
                CallQuestion.talk_to_contact.value[0],
                form.cleaned_data['talk_to_contact'],
            )
            save_call_response(
                call,
                CallQuestion.take_action.value[0],
                form.cleaned_data['take_action'],
            )
            save_call_response(
                call,
                CallQuestion.talk_to_contact_why_not.value[0],
                form.cleaned_data['talk_to_contact_why_not'],
            )
            save_call_response(
                call,
                CallQuestion.voice_message.value[0],
                form.cleaned_data['voice_message'],
            )
            save_call_response(
                call,
                CallQuestion.opt_out.value[0],
                form.cleaned_data['opt_out'],
            )

            messages.success(
                self.request,
                "Call response saved successfully."
            )

            """Redirect to Dashboard if exit flag is True"""
            if form.cleaned_data['exit_after_call'] is True:
                return redirect('organizing-hub-call-dashboard')

        """Return Call page"""
        context = self.get_context_data()

        if not self.can_access(
            context['call_campaign'],
            context['call'],
        ):
            return redirect('organizing-hub-call-dashboard')

        if context['call'] is None:
            messages.info(
                self.request,
                "No more contacts left to call for this campaign."
            )
            return redirect('organizing-hub-call-dashboard')

        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        """Only accept POST requests, otherwise redirect"""
        return redirect('organizing-hub-call-dashboard')

    def get_context_data(self, **kwargs):
        context = super(CallView, self).get_context_data(**kwargs)

        """Get Call Campaign"""
        campaign_uuid = self.kwargs['uuid']
        call_campaign = CallCampaign.objects.filter(uuid=campaign_uuid).first()
        context['call_campaign'] = call_campaign

        """Get or create Call if Caller has access to Campaign"""
        user = self.request.user
        if self.can_access(call_campaign, call=None) and hasattr(
            user,
            'callprofile',
        ):
            """Find or create active Call for caller"""
            caller = user.callprofile
            call = find_or_create_active_call_for_campaign_and_caller(
                call_campaign,
                caller,
            )
        else:
            call = None
        context['call'] = call

        """Get Call Form for Call"""
        if call is not None:
            """TODO: include existing Call Responses?"""
            call_form = CallForm(initial={'call_uuid': call.uuid})
        else:
            call_form = None
        context['form'] = call_form

        """Check if User can manage Call Campaign"""
        context['can_manage_campaign'] = can_change_call_campaign(
            user,
            call_campaign,
        )

        return context


class CallCampaignCreateView(
    LocalGroupPermissionRequiredMixin,
    SuccessMessageMixin,
    CreateView
):
    form_class = CallCampaignForm
    model = CallCampaign
    organizing_hub_feature = OrganizingHubFeature.calling_tool
    permission_required = 'calls.add_callcampaign'
    success_message = '''
    Your calling campaign request has been submitted and will be reviewed by
    our team.
    '''

    def form_valid(self, form):
        """Set local group and owner before save"""
        form.instance.local_group = self.get_local_group()
        form.instance.owner = self.request.user.callprofile

        """Take comma separated caller emails and get or create corresponding
        call profiles"""
        caller_emails = form.cleaned_data['caller_emails']

        """Save call_campaign because we need a primary key in order to save
        Many-to-many caller relationships"""
        call_campaign = form.save()
        caller_ids = get_or_create_callers(caller_emails)
        form.instance.callers = caller_ids

        return super(CallCampaignCreateView, self).form_valid(form)

    def get_local_group(self):
        if self.local_group is None:
            self.local_group = find_local_group_by_user(self.request.user)
        return self.local_group

    def get_initial(self, *args, **kwargs):
        initial = {
            'max_distance': min(25, CALLS_MAX_DISTANCE_MILES),
            'max_recipients': min(100, CALLS_MAX_LIST_SIZE),
            'script': campaign_script_template,
        }
        return initial

    def get_success_url(self):
        return reverse_lazy(
            'organizing-hub-call-campaign-detail',
            kwargs={'uuid': self.object.uuid}
        )


class CallCampaignDetailView(LocalGroupPermissionRequiredMixin, DetailView):
    context_object_name = 'campaign'
    model = CallCampaign
    organizing_hub_feature = OrganizingHubFeature.calling_tool
    permission_required = 'calls.change_callcampaign'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_local_group(self):
        """Get Local Group attached to Call Campaign"""
        if self.local_group is None:
            call_campaign = self.get_object()
            self.local_group = call_campaign.local_group
        return self.local_group


class CallCampaignDownloadView(LocalGroupPermissionRequiredMixin, DetailView):
    model = CallCampaign
    organizing_hub_feature = OrganizingHubFeature.calling_tool
    permission_required = 'calls.change_callcampaign'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get(self, request, *args, **kwargs):
        """Only accept POST requests, otherwise redirect"""
        return redirect(
            'organizing-hub-call-campaign-detail',
            self.kwargs['uuid']
        )

    def get_local_group(self):
        """Get Local Group attached to Call Campaign"""
        if self.local_group is None:
            call_campaign = self.get_object()
            self.local_group = call_campaign.local_group
        return self.local_group

    def post(self, request, *args, **kwargs):

        """Redirect if Call Campaign does not have data download"""
        call_campaign = self.get_object()
        if not call_campaign.has_data_download:
            return redirect(
                'organizing-hub-call-campaign-detail',
                self.kwargs['uuid']
            )

        """Get Calls made for Campaign so we can generate CSV data"""
        calls_made = find_calls_made_by_campaign(call_campaign)

        """Start CSV file"""
        response = HttpResponse(content_type='text/csv')
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        filename = 'call-campaign-%s-%s.csv' % (call_campaign.uuid, timestamp)
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        writer = unicodecsv.writer(response, encoding='utf-8')

        """Add header row to CSV"""
        header_row = [
            'First Name',
            'Last Name',
            'Response',
            'Phone',
            'Email',
            'Opt Out',
        ]
        writer.writerow(header_row)

        """Loop through Calls made and add relevant data to CSV"""
        for call in calls_made:
            call_row = []
            contact = call.contact

            """Always add First and Last Name"""
            call_row.append(contact.first_name)
            call_row.append(contact.last_name)

            """Find Response to Take Action question and add Answer to CSV"""
            take_action_response = call.callresponse_set.filter(
                question=CallQuestion.take_action.value[0]
            ).first()
            if take_action_response is not None:
                call_row.append(take_action_response.get_answer_display())
            else:
                call_row.append('')

            """Check if phone number is on our Opt Out list"""
            has_opt_out = contact.phone_number is not None and (
                has_phone_opt_out(contact.phone_number, OptOutType.calling)
            )

            """Add phone/email if not opted out and wants to take action"""
            if not has_opt_out and take_action_response is not None and (
                take_action_response.answer == CallAnswer.yes.value[0]
            ):
                call_row.append(contact.phone_number)
                call_row.append(contact.email_address)
            else:
                call_row.append('')
                call_row.append('')

            """Add Opt Out"""
            if has_opt_out:
                call_row.append(has_opt_out)
            else:
                call_row.append('')

            """Write Call data to CSV"""
            writer.writerow(call_row)

        """Return CSV"""
        return response


class CallCampaignUpdateView(
    LocalGroupPermissionRequiredMixin,
    SuccessMessageMixin,
    UpdateView
):
    context_object_name = 'campaign'
    template_name = "calls/callcampaign_form.html"
    form_class = CallCampaignUpdateForm
    model = CallCampaign
    organizing_hub_feature = OrganizingHubFeature.calling_tool
    permission_required = 'calls.change_callcampaign'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    success_message = '''
    Your calling campaign has been edited succesfully.
    '''

    def form_valid(self, form):
        caller_emails = form.cleaned_data['caller_emails']
        caller_ids = get_or_create_callers(caller_emails)
        form.instance.callers = caller_ids
        return super(CallCampaignUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CallCampaignUpdateView, self).get_context_data(**kwargs)
        context['update_view'] = True
        return context

    def get_initial(self, *args, **kwargs):
        call_campaign = self.get_object()
        caller_emails = []

        """Build list of caller emails to populate form with instead of IDs"""
        for caller in call_campaign.callers.all():
            caller_emails.append(str(caller.user.email))

        """Parse list of caller emails to comma separated values string"""
        caller_emails_string = ", ".join(caller_emails)

        initial = {
            'caller_emails': caller_emails_string,
        }
        return initial

    def get_local_group(self):
        campaign = self.get_object()
        return campaign.local_group

    def get_success_url(self):
        return reverse_lazy(
            'organizing-hub-call-campaign-detail',
            kwargs={'uuid': self.object.uuid}
        )


@method_decorator(verified_email_required, name='dispatch')
class CallDashboardView(TemplateView):
    template_name = "calls/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super(CallDashboardView, self).get_context_data(**kwargs)

        """Find campaigns as admin or caller"""
        user = self.request.user
        if hasattr(user, 'callprofile'):
            call_profile = user.callprofile
        else:
            """Create call profile if doesn't exist"""
            call_profile = CallProfile.objects.create(user=user)

        campaigns_as_admin = find_campaigns_as_admin(call_profile)
        campaigns_as_admin_sorted = sorted(
            campaigns_as_admin,
            key=lambda x: x.is_in_progress,
            reverse=True,
        )
        campaigns_as_admin_active = [(
            x,
            CallForm() if x.is_in_progress else None
        ) for x in campaigns_as_admin_sorted if x.is_active]

        campaigns_as_admin_inactive = [
            (x, None) for x in campaigns_as_admin_sorted if not x.is_active
        ]

        campaigns_as_caller = find_campaigns_as_caller(call_profile)
        campaigns_as_caller_sorted = sorted(
            campaigns_as_caller,
            key=lambda x: x.is_in_progress,
            reverse=True,
        )
        campaigns_as_caller_active = [(
            x,
            CallForm() if x.is_in_progress else None
        ) for x in campaigns_as_caller_sorted if (
            x.is_active and x not in campaigns_as_admin
        )]

        context['campaigns_as_admin_active'] = campaigns_as_admin_active
        context['campaigns_as_admin_inactive'] = campaigns_as_admin_inactive
        context['campaigns_as_caller_active'] = campaigns_as_caller_active

        """Check if User can create or manage Call Campaigns"""
        local_group = find_local_group_by_user(user)
        context['local_group'] = local_group
        context['can_add_campaign'] = has_call_permission_for_local_group(
            user,
            local_group,
            'calls.add_callcampaign',
        )
        context['can_manage_campaign'] = has_call_permission_for_local_group(
            user,
            local_group,
            'calls.change_callcampaign',
        )

        return context


class CallCampaignStatusView(LocalGroupPermissionRequiredMixin, DetailView):
    context_object_name = 'call_campaign'
    template_name = "calls/callcampaign_status.html"
    model = CallCampaign
    organizing_hub_feature = OrganizingHubFeature.calling_tool
    permission_required = 'calls.change_callcampaign'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get(self, request, *args, **kwargs):
        """Check if there is a valid action, otherwise redirect"""
        if self.is_valid_change(request, *args, **kwargs):
            return super(CallCampaignStatusView, self).get(
                request,
                *args,
                **kwargs
            )
        else:
            return redirect(
                'organizing-hub-call-campaign-detail',
                self.kwargs['uuid']
            )

    def get_context_data(self, **kwargs):
        context = super(CallCampaignStatusView, self).get_context_data(**kwargs)
        call_campaign = self.get_object()

        """Get status id"""
        status_id = int(self.kwargs['status_id'])

        """Get action"""
        if call_campaign.status == CallCampaignStatus.approved.value[0] and (
            status_id == CallCampaignStatus.in_progress.value[0]
        ):
            context['action'] = "Start Campaign"
        elif call_campaign.status == CallCampaignStatus.in_progress.value[0] and (
            status_id == CallCampaignStatus.paused.value[0]
        ):
            context['action'] = "Pause Campaign"
        elif call_campaign.status == CallCampaignStatus.paused.value[0] and (
            status_id == CallCampaignStatus.in_progress.value[0]
        ):
            context['action'] = "Resume Campaign"
        elif call_campaign.status in [
            CallCampaignStatus.in_progress.value[0],
            CallCampaignStatus.paused.value[0],
        ] and (
            status_id == CallCampaignStatus.complete.value[0]
        ):
            context['action'] = "Complete Campaign"

        return context

    def get_local_group(self):
        """Get Local Group attached to Call Campaign"""
        if self.local_group is None:
            call_campaign = self.get_object()
            self.local_group = call_campaign.local_group
        return self.local_group

    def post(self, request, *args, **kwargs):

        """Check if change is valid"""
        if self.is_valid_change(request, *args, **kwargs):

            call_campaign = self.get_object()

            """Get status id"""
            status_id = int(self.kwargs['status_id'])

            call_campaign.status = status_id
            call_campaign.save()
            messages.success(
                self.request,
                "Status saved successfully."
            )

        return redirect(
            'organizing-hub-call-campaign-detail',
            self.kwargs['uuid']
        )

    def is_valid_change(self, request, *args, **kwargs):
        """Check if old and new statuses represent a valid status transition"""
        call_campaign = self.get_object()

        """Get status id"""
        status_id = int(self.kwargs['status_id'])

        if call_campaign.status == CallCampaignStatus.approved.value[0] and (
            status_id == CallCampaignStatus.in_progress.value[0]
        ):
            valid_change = True
        elif call_campaign.status == CallCampaignStatus.in_progress.value[0] and (
            status_id == CallCampaignStatus.paused.value[0]
        ):
            valid_change = True
        elif call_campaign.status == CallCampaignStatus.paused.value[0] and (
            status_id == CallCampaignStatus.in_progress.value[0]
        ):
            valid_change = True
        elif call_campaign.status in [
            CallCampaignStatus.in_progress.value[0],
            CallCampaignStatus.paused.value[0],
        ] and (
            status_id == CallCampaignStatus.complete.value[0]
        ):
            valid_change = True
        else:
            valid_change = False

        return valid_change
