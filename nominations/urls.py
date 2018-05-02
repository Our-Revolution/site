from django.conf.urls import include, url
from .views import CreateApplicationView, NominationsIndexView, EditNominationView, logout, DashboardView, CandidateDashboardView, ApplicationView, EditQuestionnaireView, QuestionnaireIndexView, CandidateQuestionnaireView, SubmitView, CandidateSubmitView, handle_candidate_callback, candidate_login, ApplicationTypeView, CreateInitiativeView, reset_questionnaire
from django.views.generic import TemplateView
from .decorators import is_authenticated, is_authenticated_candidate

# placeholder urls to code templates
urlpatterns = [
    url(r'^groups/nominations/', include([
        url(
            r'^submit/$',
            SubmitView.as_view(),
            name='nominations-submit',
        ),
        url(r'^success/$', TemplateView.as_view(template_name='success.html')),
        url(r'^email-success/$', TemplateView.as_view(template_name='email-success.html')),
        url(
            r'^dashboard/$',
            DashboardView.as_view(),
            name='nominations-dashboard'
        ),
        url(r'^logout/$', is_authenticated(logout)),
        url(r'^verify/$', TemplateView.as_view(template_name='verify.html')),
        url(r'^application/$', ApplicationView.as_view()),
        url(
            r'^questionnaire/$',
            is_authenticated(QuestionnaireIndexView.as_view()),
            name='nominations-questionnaire'
        ),
        url(r'^new/$', CreateApplicationView.as_view()),
        url(r'^application-type/$', ApplicationTypeView.as_view()),
        url(r'^nomination/$', EditNominationView.as_view()),
        url(
            r'^questionnaire/edit$',
            EditQuestionnaireView.as_view(),
            name='nominations-questionnaire-edit'
        ),
        url(
            r'^questionnaire/reset$',
            reset_questionnaire,
            name='nominations-questionnaire-reset'
        ),
        url(r'^$', NominationsIndexView.as_view()),
    ])),
    url(r'^groups/nominations/candidate/', include([
        url(r'^login/$', candidate_login),
        url(r'^verify/$', TemplateView.as_view(template_name='candidate/verify.html')),
        url(r'^callback/$', handle_candidate_callback),
        url(r'^questionnaire/$', is_authenticated_candidate(CandidateQuestionnaireView.as_view())),
        url(r'^dashboard/$', is_authenticated_candidate(CandidateDashboardView.as_view())),
        url(r'^submit/$', is_authenticated_candidate(CandidateSubmitView.as_view())),
        url(r'^success/$', is_authenticated_candidate(TemplateView.as_view(template_name='candidate/success.html'))),
    ])),
    url(r'^groups/nominations/initiatives/', include([
        url(r'^new/$', CreateInitiativeView.as_view()),
        url(r'^success/$', TemplateView.as_view(template_name='success.html')),
    ])),
]
