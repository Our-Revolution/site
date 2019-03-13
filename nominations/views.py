from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic import (
    CreateView,
    UpdateView,
    TemplateView,
    DetailView,
    FormView
)
from django.http import HttpResponseRedirect
from local_groups.models import find_local_group_by_user
from organizing_hub.decorators import verified_email_required
from organizing_hub.mixins import LocalGroupPermissionRequiredMixin
from .forms import (
    ApplicationForm,
    NominationForm,
    NominationResponseFormset,
    NominationResponseFormsetHelper,
    PrioritySupportForm,
    QuestionnaireForm,
    QuestionnaireResponseFormset,
    QuestionnaireResponseFormsetHelper,
    CandidateEmailForm,
    InitiativeApplicationForm
)
from .models import (
    Application,
    InitiativeApplication,
    Questionnaire
)
from auth0.v3.authentication import GetToken, Users, Passwordless
from auth0.v3.management import Users as Auth0Users
import json
import os
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
import datetime
import logging

logger = logging.getLogger(__name__)


auth0_domain = settings.AUTH0_DOMAIN
auth0_client_id = settings.AUTH0_CLIENT_ID
auth0_client_secret = settings.AUTH0_CLIENT_SECRET
ELECTORAL_COORDINATOR_EMAIL = settings.ELECTORAL_COORDINATOR_EMAIL
OR_LOGO_SECONDARY = settings.OR_LOGO_SECONDARY

QUESTIONNAIRE_NOT_FOUND_ERROR = """
We couldn't find that questionnaire. Make sure you're logged in
with the correct email address and that you have access to edit the current
application.
"""


"""Methods"""


def can_candidate_access(application, email):
    """
    Can candidate access Application

    Match on the authorized email field on Application model. Do not match on
    the candidate email field on the Questionnaire model.

    Parameters
    ----------
    application : Application
        Application that is potentially being accessed
    email : str
        Candidate email address (authorized_email)

    Returns
        -------
        bool
            Returns true for access granted
    """

    authorized_email = application.authorized_email
    if authorized_email is not None and (
        authorized_email.lower() == email.lower()
    ):
        can_access = True
    else:
        can_access = False

    return can_access


def find_applications_for_candidate(email):
    """
    Find Applications for Candidate based on email address

    Match on the authorized email field on Application model. Do not match on
    the candidate email field on the Questionnaire model.

    Parameters
    ----------
    email : str
        Candidate email address (authorized_email)

    Returns
        -------
        Application list
            Returns matching Application list for candidate
    """

    applications = Application.objects.filter(
        authorized_email__iexact=email
    ).order_by('-create_dt')
    return applications


def find_applications_with_complete_questionnaires(
    candidate_last_name,
    state_or_territory,
):
    """
    Find Applications with completed Questionnaires for Local Group use

    Match on last name and state field on Questionnaire. Only match on
    Questionnaires completed by candidate. Only return recent Questionnaires.

    It is ok to treat completed Candidate Questionnaires from candidates as
    public.

    Parameters
    ----------
    candidate_last_name : str
        Candidate last name
    state_or_territory : str
        Candidate state or territory

    Returns
        -------
        Application list
            Returns matching Application list for Local Group
    """

    """Filter by last 2 years so we only show recent questionnaires"""
    date_cutoff = timezone.now() - datetime.timedelta(
        days=365*2
    )

    """Filter by authorized email not none & completed by candidate is true"""
    applications = Application.objects.filter(
        authorized_email__isnull=False,
        create_dt__gte=date_cutoff,
        questionnaire__candidate_last_name__iexact=candidate_last_name,
        questionnaire__candidate_state=state_or_territory,
        questionnaire__completed_by_candidate=True,
        questionnaire__status='complete',
    ).order_by('-create_dt')
    return applications


def get_auth0_user_id_by_email(email):
    """Get Auth0 user id by user email"""

    get_token = GetToken(auth0_domain)
    token = get_token.client_credentials(
        auth0_client_id,
        auth0_client_secret,
        'https://{}/api/v2/'.format(auth0_domain)
    )
    mgmt_api_token = token['access_token']
    auth0_users = Auth0Users(auth0_domain, mgmt_api_token)
    query = 'email:%s' % email
    results = auth0_users.list(q=query, search_engine='v3')
    if results['users']:
        auth0_user_id = results['users'][0]['user_id']
    else:
        auth0_user_id = None

    return auth0_user_id


def is_application_owner(user, application):
    """Check if a user owns an application"""

    if application.auth_user == user:
        """Check auth_user first"""
        return True

    elif not application.auth_user and application.user_id:
        """Check Auth0 for legacy applications"""
        if application.user_id == get_auth0_user_id_by_email(user.email):
            return True
        else:
            return False

    else:
        """Otherwise false"""
        return False


def send_application_submitted_notification(application):
    """
    Send email notification to group/candidate/OR for Candidate Application
    submission

    Call this method as needed when the Candidate Application changes to status
    submitted

    Parameters
    ----------
    application : CandidateApplication
        CandidateApplication
    """
    candidate_name = application.candidate_name
    if application.authorized_email is not None:
        candidate_email = application.authorized_email
    else:
        candidate_email = application.questionnaire.candidate_email

    group_name = application.group.name
    group_email = application.rep_email

    cc_emails = [
        '"%s" <%s>' % (candidate_name, candidate_email),
        '"%s" <%s>' % (
            'Our Revolution Electoral Coordinator',
            ELECTORAL_COORDINATOR_EMAIL
        ),
    ]
    from_email = '"%s" <%s>' % (
        'Our Revolution Electoral Coordinator',
        ELECTORAL_COORDINATOR_EMAIL
    )
    to_email = [
        # Use double quotes for group name
        '"%s" <%s>' % (group_name, group_email),
    ]

    subject = """
    Your nomination for %s has been submitted! Here are the next steps.
    """ % candidate_name

    d = {
        'or_logo_secondary': OR_LOGO_SECONDARY,
        'group_name': group_name,
        'candidate_name': candidate_name
    }

    html_template = get_template('email/application_submit_email.html')
    html_content = html_template.render(d)
    text_template = get_template('email/application_submit_email.txt')
    text_content = text_template.render(d)

    msg = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        to_email,
        cc=cc_emails
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def submit_application(application):
    """
    Submit Candidate Application and send email notification

    Parameters
    ----------
    application : CandidateApplication
        CandidateApplication

    Returns
        -------
        CandidateApplication
            Returns updated CandidateApplication
    """

    """Check if questionnaire and nomination are complete"""
    if application.questionnaire.status == 'complete' and (
        application.nomination.status == 'complete'
    ):

        """Update status to submitted if needed"""
        if application.is_editable() and application.status != 'submitted':
            application.status = 'submitted'
            application.save()

        """Send notification for submitted status"""
        send_application_submitted_notification(application)

    return application


"""Views"""


class NominationsIndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super(NominationsIndexView, self).get_context_data(**kwargs)
        return context


class ApplicationStartView(
    LocalGroupPermissionRequiredMixin,
    TemplateView,
):
    permission_required = 'nominations.add_application'
    skip_feature_check = True
    template_name = 'application_start.html'

    def get_local_group(self):
        if self.local_group is None:
            self.local_group = find_local_group_by_user(self.request.user)
        return self.local_group


class CreateApplicationView(
    LocalGroupPermissionRequiredMixin,
    CreateView,
):
    form_class = ApplicationForm
    permission_required = 'nominations.add_application'
    template_name = "application.html"
    skip_feature_check = True
    success_url = '/groups/nominations/application'

    def form_valid(self, form):
        """Attach user and local group to application"""
        form.instance.auth_user = self.request.user
        form.instance.group = self.get_local_group()

        super(CreateApplicationView, self).form_valid(form)

        return redirect(self.success_url + '?id=' + str(self.object.pk))

    def get_context_data(self, **kwargs):
        context = super(CreateApplicationView, self).get_context_data(**kwargs)
        context['local_group'] = self.get_local_group()
        return context

    def get_local_group(self):
        if self.local_group is None:
            self.local_group = find_local_group_by_user(self.request.user)
        return self.local_group


@method_decorator(verified_email_required, name='dispatch')
class EditNominationView(UpdateView):
    form_class = NominationForm
    template_name = "nomination.html"

    def get_object(self):
        app_id = self.request.GET.get('id')
        app = get_object_or_404(Application, pk=app_id)
        if is_application_owner(self.request.user, app):
            return app.nomination
        else:
            raise Http404(_("No nomination found matching the query"))

    def get_success_url(self):
        return "/groups/nominations/questionnaire?id=" + self.request.GET.get('id')

    def form_valid(self, form):
        form.instance.status = 'complete'
        form_valid = super(EditNominationView, self).form_valid(form)

        # save responses
        formset = NominationResponseFormset(self.request.POST or None, instance=self.object, prefix="questions")
        if formset.is_valid():
            formset.save()
        else:
            print formset.errors
            return self.form_invalid(form)

        """Submit application if questionnaire is complete too"""
        application = self.get_object().application
        if application.questionnaire.status == 'complete':
            submit_application(application)

        return form_valid

    def get_context_data(self, *args, **kwargs):
        context_data = super(EditNominationView, self).get_context_data(
            *args,
            **kwargs
        )
        context_data['formset'] = NominationResponseFormset(
            self.request.POST or None,
            instance=self.object,
            prefix="questions"
        )
        context_data['helper'] = NominationResponseFormsetHelper()
        context_data['application'] = self.object.application
        return context_data


@method_decorator(verified_email_required, name='dispatch')
class EditQuestionnaireView(UpdateView):
    form_class = QuestionnaireForm
    template_name = "questionnaire.html"

    def get_application(self):
        app_id = self.request.GET.get('id')
        app = get_object_or_404(Application, pk=app_id)
        if is_application_owner(self.request.user, app):
            return app
        else:
            raise Http404(_("No application found matching the query"))

    def get_object(self):
        app = self.get_application()
        if is_application_owner(self.request.user, app):
            return app.questionnaire
        else:
            raise Http404(_("No questionnaire found matching the query"))

    def get_success_url(self):
        return reverse_lazy('nominations-application') + "?id=" + self.request.GET.get('id')

    def form_valid(self, form):

        """Get responses and validate them too"""
        formset = QuestionnaireResponseFormset(
            self.request.POST or None,
            instance=self.object,
            prefix="questions",
        )
        if formset.is_valid():

            """Save responses"""
            formset.save()

            """Set status to complete and save questionnaire"""
            form.instance.status = 'complete'
            form_valid = super(EditQuestionnaireView, self).form_valid(form)

            """Submit application if nomination is complete too"""
            application = self.get_application()
            if application.nomination.status == 'complete':
                submit_application(application)

            return form_valid

        else:
            """If responses are invalid then return errors"""
            return self.form_invalid(form)

    def get_context_data(self, *args, **kwargs):
        context_data = super(EditQuestionnaireView, self).get_context_data(
            *args,
            **kwargs
        )
        context_data['formset'] = QuestionnaireResponseFormset(
            self.request.POST or None,
            instance=self.object,
            prefix="questions"
        )
        context_data['helper'] = QuestionnaireResponseFormsetHelper()
        context_data['application'] = self.get_application()
        context_data['questionnaire'] = self.get_object()
        return context_data


@method_decorator(verified_email_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def can_create_application(self):

        """Check local group permission"""
        permission = 'nominations.add_application'
        user = self.request.user
        local_group = find_local_group_by_user(user)
        if local_group is not None:
            can_create = user.localgroupprofile.has_permission_for_local_group(
                local_group,
                permission
            )
        else:
            can_create = False

        return can_create

    def get_context_data(self, *args, **kwargs):
        context_data = super(DashboardView, self).get_context_data(
            *args,
            **kwargs
        )

        """Get both legacy auth0 applications and new applications"""
        auth0_user_id = get_auth0_user_id_by_email(self.request.user.email)
        if auth0_user_id:
            context_data['applications'] = Application.objects.all().filter(
                Q(auth_user_id=self.request.user.id) | Q(user_id=auth0_user_id)
            ).order_by('-create_dt')
            context_data['initiative_applications'] = InitiativeApplication.objects.all(
            ).filter(
                Q(auth_user_id=self.request.user.id) | Q(user_id=auth0_user_id)
            ).order_by('-create_dt')
        else:
            context_data['applications'] = Application.objects.all().filter(
                auth_user_id=self.request.user.id
            ).order_by('-create_dt')
            context_data['initiative_applications'] = InitiativeApplication.objects.all(
            ).filter(auth_user_id=self.request.user.id).order_by('-create_dt')

        """Check if user can create new application"""
        context_data['can_create_application'] = self.can_create_application()

        return context_data


@method_decorator(verified_email_required, name='dispatch')
class ApplicationView(DetailView):
    template_name = 'application_status.html'

    def get_object(self):
        app_id = self.request.GET.get('id')
        app = get_object_or_404(Application, pk=app_id)
        if is_application_owner(self.request.user, app):
            return app
        else:
            raise Http404(_("No application found matching the query"))

    def get_context_data(self, *args, **kwargs):
        context_data = super(ApplicationView, self).get_context_data(
            *args,
            **kwargs
        )
        context_data['application'] = self.object
        return context_data


class PrioritySupportView(
    # LocalGroupPermissionRequiredMixin,
    # SuccessMessageMixin,
    UpdateView
):
    context_object_name = 'application'
    template_name = "priority_support.html"
    form_class = PrioritySupportForm
    model = Application
    # organizing_hub_feature = OrganizingHubFeature.call_tool
    # permission_required = 'calls.change_callcampaign'
    # slug_field = 'uuid'
    # slug_url_kwarg = 'uuid'
    # success_message = '''
    # lebowski
    # '''

    # def form_valid(self, form):
    #     caller_emails = form.cleaned_data['caller_emails']
    #     caller_ids = get_or_create_callers(caller_emails)
    #     form.instance.callers = caller_ids
    #     return super(CallCampaignUpdateView, self).form_valid(form)

    # def get_context_data(self, **kwargs):
    #     context = super(CallCampaignUpdateView, self).get_context_data(**kwargs)
    #     context['update_view'] = True
    #     return context

    # def get_initial(self, *args, **kwargs):
    #     call_campaign = self.get_object()
    #     caller_emails = []
    #
    #     """Build list of caller emails to populate form with instead of IDs"""
    #     for caller in call_campaign.callers.all():
    #         caller_emails.append(str(caller.user.email))
    #
    #     """Parse list of caller emails to comma separated values string"""
    #     caller_emails_string = ", ".join(caller_emails)
    #
    #     initial = {
    #         'caller_emails': caller_emails_string,
    #     }
    #     return initial

    # def get_local_group(self):
    #     campaign = self.get_object()
    #     return campaign.local_group

    # def get_success_url(self):
    #     return reverse_lazy(
    #         'organizing-hub-call-campaign-detail',
    #         kwargs={'uuid': self.object.uuid}
    #     )


@method_decorator(verified_email_required, name='dispatch')
class QuestionnaireIndexView(FormView):
    form_class = CandidateEmailForm
    template_name = 'questionnaire_index.html'

    def get_success_url(self):
        return "/groups/nominations/email-success"

    def form_valid(self, form):
        application = self.get_application()

        candidate_name = application.candidate_first_name + ' ' + application.candidate_last_name
        candidate_email = form.cleaned_data['candidate_email']
        group_name = application.group.name
        rep_email = application.rep_email

        application.authorized_email = candidate_email
        application.questionnaire.status = 'sent'
        application.save()
        application.questionnaire.save()

        plaintext = get_template('email/candidate_email.txt')
        htmly = get_template('email/candidate_email.html')

        candidate_dashboard_url = self.request.build_absolute_uri(
            reverse('nominations-candidate-dashboard')
        )

        d = {
            'candidate_dashboard_url': candidate_dashboard_url,
            'candidate_name': candidate_name,
            'group_name': group_name,
            'group_rep_email': rep_email,
            'or_logo_secondary': OR_LOGO_SECONDARY,
        }

        subject = "You're being nominated for endorsement by an official Our Revolution group!"
        from_email = 'Our Revolution <info@ourrevolution.com>'
        to_email = ['"%s" <%s>' % (candidate_name, candidate_email)]
        cc_emails = [
            # Use double quotes for group name
            '"%s" <%s>' % (group_name, rep_email),
            '"%s" <%s>' % (
                'Our Revolution National',
                ELECTORAL_COORDINATOR_EMAIL
            )
        ]

        text_content = plaintext.render(d)
        html_content = htmly.render(d)
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            to_email,
            cc=cc_emails
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        return super(QuestionnaireIndexView, self).form_valid(form)

    def get_application(self):
        app_id = self.request.GET.get('id')
        app = get_object_or_404(Application, pk=app_id)
        if is_application_owner(self.request.user, app):
            return app
        else:
            raise Http404(_("No application found matching the query"))

    def get_object(self):
        app = self.get_application()
        if is_application_owner(self.request.user, app):
            return app.questionnaire
        else:
            raise Http404(_("No questionnaire found matching the query"))

    def get_context_data(self, *args, **kwargs):
        context_data = super(QuestionnaireIndexView, self).get_context_data(
            *args,
            **kwargs
        )
        application = self.get_application()
        context_data['application'] = application

        applications_complete = find_applications_with_complete_questionnaires(
            candidate_last_name=application.candidate_last_name,
            state_or_territory=application.candidate_state,
        )
        context_data['applications_complete'] = applications_complete

        return context_data


@method_decorator(verified_email_required, name='dispatch')
class QuestionnaireSelectView(DetailView):
    model = Application

    def get(self, request, *args, **kwargs):
        """Redirect on GET. Should be POST only."""
        return redirect(reverse_lazy(
            'nominations-application'
        ) + "?id=" + self.kwargs['pk'])

    def get_success_url(self):
        return reverse_lazy(
            'nominations-application'
        ) + "?id=" + self.kwargs['pk']

    def post(self, request, *args, **kwargs):

        """Check access and status"""
        application = self.get_object()
        app_complete = Application.objects.filter(
            pk=self.kwargs['app_complete']
        ).first()
        if is_application_owner(self.request.user, application) and (
            application.questionnaire.status != 'complete'
        ) and app_complete is not None and (
            app_complete.authorized_email is not None
        ) and app_complete.questionnaire.completed_by_candidate and (
            app_complete.questionnaire.status == 'complete'
        ):

            """Attach authorized email & questionnaire to application"""
            application.authorized_email = app_complete.authorized_email
            application.questionnaire = app_complete.questionnaire
            application.save()

            """Submit application if nomination is complete too"""
            if application.nomination.status == 'complete':
                submit_application(application)

            return redirect(self.get_success_url())
        else:
            raise Http404(_("No application found matching the query"))


@verified_email_required
def reset_questionnaire(request):
    app_id = request.GET.get('id')
    application = get_object_or_404(Application, pk=app_id)

    if not is_application_owner(request.user, application):
        raise Http404(_("No application found matching the query"))

    questionnaire = application.questionnaire

    default_next_url = reverse_lazy(
        'nominations-questionnaire-edit'
    ) + '?id=' + app_id

    # if next query string exists, redirect there after
    next_url = request.GET.get(
        'next',
        default_next_url
    )

    """Change from sent to incomplete"""
    if questionnaire.status == 'sent':
        questionnaire.status = 'incomplete'
        application.authorized_email = None
        questionnaire.save(skip_application_save=True)
        application.save()

    return redirect(next_url)


@method_decorator(verified_email_required, name='dispatch')
class CandidateDashboardView(TemplateView):
    template_name = 'candidate/dashboard.html'

    def get_context_data(self, *args, **kwargs):
        context_data = super(CandidateDashboardView, self).get_context_data(
            *args,
            **kwargs
        )
        context_data['applications'] = find_applications_for_candidate(
            self.request.user.email
        )
        return context_data


@method_decorator(verified_email_required, name='dispatch')
class CandidateQuestionnaireView(UpdateView):
    model = Questionnaire
    form_class = QuestionnaireForm
    template_name = "candidate/questionnaire.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not self.object:
            messages.error(
                self.request,
                QUESTIONNAIRE_NOT_FOUND_ERROR
            )
            return redirect("/groups/nominations/candidate/dashboard/")
        else:
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)

    def get_application(self):
        app_id = self.kwargs['app_id']
        email = self.request.user.email

        try:
            """Check access by matching user email with application email"""
            """TODO: clean up access logic"""
            application = Application.objects.filter(
                authorized_email__iexact=email,
                pk=app_id
            ).first()
        except (Application.DoesNotExist, AttributeError):
            application = None

        return application

    def get_object(self):
        application = self.get_application()
        if application is not None:
            questionnaire = application.questionnaire
        else:
            questionnaire = None
        return questionnaire

    def get_success_url(self):
        return reverse_lazy(
            'nominations-candidate-success'
        ) + "?id=" + self.kwargs['app_id']

    def form_valid(self, form):

        # save responses
        formset = QuestionnaireResponseFormset(
            self.request.POST or None,
            instance=self.object,
            prefix="questions"
        )
        if formset.is_valid():
            formset.save()

            """Set status to complete and save questionnaire"""
            form.instance.status = 'complete'
            form.instance.completed_by_candidate = True
            form_valid = super(CandidateQuestionnaireView, self).form_valid(
                form
            )

            """Submit application if nomination is complete too"""
            application = self.get_application()
            if application.nomination.status == 'complete':
                submit_application(application)

            return form_valid

        else:
            return self.form_invalid(form)

    def get_context_data(self, *args, **kwargs):
        context_data = super(
            CandidateQuestionnaireView,
            self
        ).get_context_data(
            *args,
            **kwargs
        )
        context_data['formset'] = QuestionnaireResponseFormset(
            self.request.POST or None, instance=self.object, prefix="questions"
        )
        context_data['helper'] = QuestionnaireResponseFormsetHelper()
        context_data['questionnaire'] = self.object
        return context_data


@method_decorator(verified_email_required, name='dispatch')
class CandidateQuestionnaireSelectView(DetailView):
    model = Application
    template_name = "candidate/application.html"

    def get(self, request, *args, **kwargs):
        """Check access"""
        application = self.get_object()
        email = self.request.user.email
        if can_candidate_access(application, email) and (
            application.questionnaire.status != 'complete'
        ):

            """Check if there are any completed questionnaires"""
            self.object = application
            context_data = self.get_context_data()
            if not context_data['applications_complete']:
                return redirect(
                    'nominations-candidate-questionnaire',
                    application.id,
                )

            return super(CandidateQuestionnaireSelectView, self).get(
                request,
                *args,
                **kwargs
            )
        else:
            return redirect('nominations-candidate-dashboard')

    def get_context_data(self, *args, **kwargs):
        context_data = super(
            CandidateQuestionnaireSelectView,
            self,
        ).get_context_data(*args, **kwargs)

        """Get applications with complete questionnaires"""
        application = self.get_object()
        apps = find_applications_for_candidate(self.request.user.email)
        apps_complete = []
        for app in apps:
            if app.id != application.id:
                questionnaire = app.questionnaire
                if questionnaire is not None and (
                    questionnaire.status == 'complete'
                ):
                    apps_complete.append(app)

        context_data['applications_complete'] = apps_complete
        return context_data

    def get_success_url(self):
        return reverse_lazy('nominations-candidate-success') + "?id=" + self.kwargs['pk']

    def post(self, request, *args, **kwargs):
        """Check access and status of questionnaire"""
        application = self.get_object()
        app_complete = Application.objects.filter(
            pk=self.kwargs['app_complete']
        ).first()
        email = self.request.user.email
        if app_complete is not None and can_candidate_access(
            application,
            email,
        ) and can_candidate_access(
            app_complete,
            email,
        ) and application.questionnaire.status != 'complete' and (
            app_complete.questionnaire.status == 'complete'
        ):

            """Attach completed questionnaire to the current application"""
            application.questionnaire = app_complete.questionnaire
            application.save()

            """Submit application if nomination is complete too"""
            if application.nomination.status == 'complete':
                submit_application(application)

            return redirect(self.get_success_url())
        else:
            return redirect(
                'nominations-candidate-questionnaire-select',
                application.id,
            )


@method_decorator(verified_email_required, name='dispatch')
class CandidateSuccessView(TemplateView):
    template_name = "candidate/success.html"


# Ballot initiatives
class CreateInitiativeView(
    LocalGroupPermissionRequiredMixin,
    CreateView,
):
    form_class = InitiativeApplicationForm
    permission_required = 'nominations.add_initiativeapplication'
    template_name = "initiatives/application.html"
    skip_feature_check = True
    success_url = '/groups/nominations/initiatives/success'

    def form_valid(self, form):
        """Attach user and local group to application"""
        form.instance.auth_user = self.request.user
        form.instance.group = self.get_local_group()

        form.instance.locality = form.cleaned_data['locality']
        form.instance.status = 'submitted'

        super(CreateInitiativeView, self).form_valid(form)

        return redirect(self.success_url + '?id=' + str(self.object.pk))

    def get_context_data(self, *args, **kwargs):
        context = super(CreateInitiativeView, self).get_context_data(
            *args,
            **kwargs
        )
        context['local_group'] = self.get_local_group()
        return context

    def get_local_group(self):
        if self.local_group is None:
            self.local_group = find_local_group_by_user(self.request.user)
        return self.local_group
