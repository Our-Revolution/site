from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
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
from organizing_hub.decorators import verified_email_required
from .forms import (
    ApplicationForm,
    NominationForm,
    NominationResponseFormset,
    CandidateLoginForm,
    NominationResponseFormsetHelper,
    QuestionnaireForm,
    QuestionnaireResponseFormset,
    QuestionnaireResponseFormsetHelper,
    SubmitForm,
    CandidateEmailForm,
    CandidateSubmitForm,
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
import logging

logger = logging.getLogger(__name__)


auth0_domain = settings.AUTH0_DOMAIN
auth0_client_id = settings.AUTH0_CLIENT_ID
auth0_client_secret = settings.AUTH0_CLIENT_SECRET
auth0_candidate_callback_url = settings.AUTH0_CANDIDATE_CALLBACK_URL

QUESTIONNAIRE_NOT_FOUND_ERROR = """
We couldn't find that questionnaire. Make sure you're logged in
with the correct email address and that you have access to edit the current
application.
"""


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


class NominationsIndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super(NominationsIndexView, self).get_context_data(**kwargs)
        return context


class ApplicationTypeView(LoginRequiredMixin, TemplateView):
    template_name = 'application_type.html'


@method_decorator(verified_email_required, name='dispatch')
class CreateApplicationView(CreateView):
    form_class = ApplicationForm
    template_name = "application.html"
    success_url = '/groups/nominations/application'

    def form_valid(self, form):
        form.instance.auth_user = self.request.user
        super(CreateApplicationView, self).form_valid(form)

        return redirect(self.success_url + '?id=' + str(self.object.pk))


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
    success_url = "/groups/nominations/submit"

    def get_object(self):
        app_id = self.request.GET.get('id')
        app = get_object_or_404(Application, pk=app_id)
        if is_application_owner(self.request.user, app):
            return app.questionnaire
        else:
            raise Http404(_("No questionnaire found matching the query"))

    def get_success_url(self):
        return "/groups/nominations/submit?id=" + self.request.GET.get('id')

    def form_valid(self, form):
        form.instance.status = 'complete'
        form_valid = super(EditQuestionnaireView, self).form_valid(form)

        # save responses
        formset = QuestionnaireResponseFormset(self.request.POST or None, instance=self.object, prefix="questions")
        if formset.is_valid():
            formset.save()
        else:
            print formset.errors
            return self.form_invalid(form)

        return form_valid

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
        context_data['application'] = self.object.application_set.first()
        context_data['questionnaire'] = self.object
        return context_data


@method_decorator(verified_email_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'dashboard.html'

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


@method_decorator(verified_email_required, name='dispatch')
class QuestionnaireIndexView(FormView):
    form_class = CandidateEmailForm
    template_name = 'questionnaire_index.html'

    def get_success_url(self):
        return "/groups/nominations/email-success"

    def form_valid(self, form):
        application = self.get_object().application_set.first()

        candidate_name = application.candidate_first_name + ' ' + application.candidate_last_name
        candidate_email = form.cleaned_data['candidate_email']
        group_name = application.group
        rep_email = application.rep_email

        application.authorized_email = candidate_email
        application.questionnaire.status = 'sent'
        application.save()
        application.questionnaire.save()

        plaintext = get_template('email/candidate_email.txt')
        htmly = get_template('email/candidate_email.html')

        d = {
            'group_name': group_name,
            'candidate_name': candidate_name,
            'group_rep_email': rep_email,
            'or_logo_secondary': settings.OR_LOGO_SECONDARY,
        }

        subject = "You're being nominated for endorsement by an official Our Revolution group!"
        from_email = 'Our Revolution <info@ourrevolution.com>'
        to_email = ["%s <%s>" % (candidate_name, candidate_email)]
        cc_emails = [
            "%s <%s>" % (group_name, rep_email),
            "%s <%s>" % (
                'Our Revolution National',
                settings.ELECTORAL_COORDINATOR_EMAIL
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

    def get_object(self):
        app_id = self.request.GET.get('id')
        app = get_object_or_404(Application, pk=app_id)
        if is_application_owner(self.request.user, app):
            return app.questionnaire
        else:
            raise Http404(_("No questionnaire found matching the query"))

    def get_context_data(self, *args, **kwargs):
        context_data = super(QuestionnaireIndexView, self).get_context_data(
            *args,
            **kwargs
        )
        context_data['application'] = self.get_object().application_set.first()
        return context_data


@method_decorator(verified_email_required, name='dispatch')
class SubmitView(FormView):
    template_name = 'submit.html'
    form_class = SubmitForm
    success_url = '/groups/nominations/success'

    # TODO: add conditional for candidate submission

    def form_valid(self, form):
        application = self.get_object()
        application.status = 'submitted'
        application.save()

        """Send notification after submit"""
        self.send_notification(application)

        return super(SubmitView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context_data = super(SubmitView, self).get_context_data(
            *args,
            **kwargs
        )
        context_data['application'] = self.get_object()
        return context_data

    def get_object(self):
        app_id = self.request.GET.get('id')
        app = get_object_or_404(Application, pk=app_id)
        if is_application_owner(self.request.user, app):
            return app
        else:
            raise Http404(_("No application found matching the query"))

    def send_notification(self, application):
        """
        Send email notification for submission to group, candidate, and OR.
        """
        candidate_name = application.candidate_name
        candidate_email = application.authorized_email
        group_name = application.group.name
        group_email = application.rep_email

        cc_emails = [
            "%s <%s>" % (candidate_name, candidate_email),
            "%s <%s>" % (
                'Our Revolution Electoral Coordinator',
                settings.ELECTORAL_COORDINATOR_EMAIL
            ),
        ]
        from_email = "%s <%s>" % (
            'Our Revolution Electoral Coordinator',
            settings.ELECTORAL_COORDINATOR_EMAIL
        )
        to_email = [
            "%s <%s>" % (group_name, group_email),
        ]

        subject = """
        Your nomination for %s has been submitted! Here are the next steps.
        """ % candidate_name

        d = {
            'or_logo_secondary': settings.OR_LOGO_SECONDARY,
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


def logout(request):
    request.session.clear()
    base_url = 'https://ourrevolution.com/groups/nominations'
    return redirect('https://%s/v2/logout?returnTo=%s&client_id=%s' % (auth0_domain, base_url, auth0_client_id))


# Candidate Facing Dashboard
def candidate_login(request):
    # if user is already logged in
    if 'profile' in request.session:
        return redirect('/groups/nominations/candidate/dashboard?c=1')

    if request.method == 'POST':
        form = CandidateLoginForm(request.POST)

        if form.is_valid():
            # initiatie Auth0 passwordless
            passwordless = Passwordless(auth0_domain)

            email = form.cleaned_data['email']
            passwordless.email(auth0_client_id,email,auth_params={'response_type':'code','redirect_uri':auth0_candidate_callback_url})

            return HttpResponseRedirect('/groups/nominations/candidate/verify')

    else:
        form = CandidateLoginForm()

    return render(request, 'candidate/login.html', {'form': form})


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

    questionnaire.status = 'incomplete'
    application.authorized_email = None
    questionnaire.save(skip_application_save=True)
    application.save()

    return redirect(next_url)


def handle_candidate_callback(request):
    code = request.GET.get('code')

    if code:
        get_token = GetToken(auth0_domain)
        auth0_users = Users(auth0_domain)
        token = get_token.authorization_code(auth0_client_id,
                                             auth0_client_secret, code, auth0_candidate_callback_url)
        user_info = auth0_users.userinfo(token['access_token'])
        user = json.loads(user_info)
        request.session['profile'] = user

        # find application where this email is authorized to access
        application = Application.objects.all().filter(authorized_email__iexact=user['email']).first()

        return redirect('/groups/nominations/candidate/dashboard?c=1')

    messages.error(request, "That link is expired or has already been used - login again to request another. Please contact info@ourrevolution.com if you need help.")
    return redirect('/groups/nominations/candidate/dashboard?c=1')


class CandidateDashboardView(TemplateView):
    template_name = 'candidate/dashboard.html'

    def get_context_data(self, *args, **kwargs):
        user = self.request.session['profile']


        logger.debug('Candidate Dashboard:')
        logger.debug('user:')
        logger.debug(user)

        logger.debug('user email:')
        logger.debug(user['email'])

        context_data = super(CandidateDashboardView, self).get_context_data(*args, **kwargs)
        context_data['user'] = user
        context_data['applications'] = Application.objects.all().filter(authorized_email__iexact=user['email'])

        logger.debug('applications:')
        logger.debug(context_data['applications'])

        return context_data


class CandidateQuestionnaireView(UpdateView):
    model = Questionnaire
    form_class = QuestionnaireForm
    template_name = "candidate/questionnaire.html"
    success_url = "/groups/nominations/candidate/submit"

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

    def get_object(self):
        app_id = self.request.GET.get('id')
        user = self.request.session['profile']
        email = user['email']

        try:
            application = Application.objects.all().filter(
                authorized_email__iexact=email,
                pk=app_id
            ).first()
            questionnaire = application.questionnaire
        except (Application.DoesNotExist, AttributeError):
            questionnaire = None

        return questionnaire

    def get_success_url(self):
        return "/groups/nominations/candidate/submit?id=" + self.request.GET.get('id')

    def form_valid(self, form):
        form_valid = super(CandidateQuestionnaireView, self).form_valid(form)

        # save responses
        formset = QuestionnaireResponseFormset(
            self.request.POST or None,
            instance=self.object,
            prefix="questions"
        )
        if formset.is_valid():
            formset.save()
        else:
            print formset.errors
            return self.form_invalid(form)

        return form_valid

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
        context_data['user'] = self.request.session['profile']
        context_data['questionnaire'] = self.object
        return context_data


class CandidateSubmitView(FormView):
    template_name = 'candidate/submit.html'
    form_class = CandidateSubmitForm
    success_url = '/groups/nominations/candidate/success'

    def form_valid(self, form):
        app_id = self.request.GET.get('id')
        email = self.request.session['profile']['email']

        application = Application.objects.all().filter(authorized_email__iexact=email,pk=app_id).first()

        application.questionnaire.status = 'complete'
        application.questionnaire.completed_by_candidate = True
        application.questionnaire.save()

        rep_email = application.rep_email
        rep_name = application.rep_first_name + ' ' + application.rep_last_name
        candidate_name = application.candidate_first_name + ' ' + application.candidate_last_name
        nominations_submit_url = self.request.build_absolute_uri(
            reverse_lazy('nominations-submit') + ('?id=%i' % application.id)
        )

        # send email to group
        plaintext = get_template('email/group_email.txt')
        htmly     = get_template('email/group_email.html')

        d = {
            'rep_name': rep_name,
            'candidate_name': candidate_name,
            'nominations_submit_url': nominations_submit_url,
            'or_logo_secondary': settings.OR_LOGO_SECONDARY,
        }

        subject= candidate_name + " has completed your candidate questionnaire!"
        from_email='Our Revolution <info@ourrevolution.com>'
        to_email=["%s <%s>" % (rep_name,rep_email)]

        text_content = plaintext.render(d)
        html_content = htmly.render(d)
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        return super(CandidateSubmitView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        app_id = self.request.GET.get('id')
        email = self.request.session['profile']['email']
        self.app = get_object_or_404(Application, pk=app_id,authorized_email__iexact=email)
        context_data = super(CandidateSubmitView, self).get_context_data(*args, **kwargs)
        context_data['application'] = self.app
        context_data['user'] = self.request.session['profile']
        return context_data


# Ballot initiatives
@method_decorator(verified_email_required, name='dispatch')
class CreateInitiativeView(CreateView):
    form_class = InitiativeApplicationForm
    template_name = "initiatives/application.html"
    success_url = '/groups/nominations/initiatives/success'

    def form_valid(self, form):
        form.instance.auth_user = self.request.user
        form.instance.locality = form.cleaned_data['locality']
        form.instance.status = 'submitted'

        super(CreateInitiativeView, self).form_valid(form)

        return redirect(self.success_url + '?id=' + str(self.object.pk))

    def get_context_data(self, *args, **kwargs):
        context_data = super(CreateInitiativeView, self).get_context_data(
            *args,
            **kwargs
        )
        return context_data
