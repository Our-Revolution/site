from django.conf.urls import include, url
from .views import CreateApplicationView, NominationsIndexView, EditNominationView, handle_auth0_callback, logout, login, DashboardView, CandidateDashboardView, ApplicationView, EditQuestionnaireView, QuestionnaireIndexView, CandidateQuestionnaireView, SubmitView, CandidateSubmitView, handle_candidate_callback, candidate_login, ApplicationTypeView, CreateInitiativeView
from django.views.generic import TemplateView
from .decorators import is_authenticated

# placeholder urls to code templates
urlpatterns = [
    url(r'^groups/nominations/', include([
        url(r'^submit/$', is_authenticated(SubmitView.as_view())),
        url(r'^success/$', is_authenticated(TemplateView.as_view(template_name='success.html'))),
        url(r'^email-success/$', is_authenticated(TemplateView.as_view(template_name='email-success.html'))),
        url(r'^dashboard/$', is_authenticated(DashboardView.as_view())),
        url(r'^login/$', login),
        url(r'^logout/$', is_authenticated(logout)),
        url(r'^callback/$', handle_auth0_callback),
        url(r'^verify/$', TemplateView.as_view(template_name='verify.html')),
        url(r'^application/$', is_authenticated(ApplicationView.as_view())),
        url(r'^questionnaire/$', is_authenticated(QuestionnaireIndexView.as_view())),
        url(r'^new/$', is_authenticated(CreateApplicationView.as_view())),
        url(r'^application-type/$', is_authenticated(ApplicationTypeView.as_view())),
        url(r'^nomination/$', is_authenticated(EditNominationView.as_view())),
        url(r'^questionnaire/edit$', is_authenticated(EditQuestionnaireView.as_view())),
        url(r'^$', NominationsIndexView.as_view()),
    ])),
    url(r'^groups/nominations/candidate/', include([
        url(r'^login/$', candidate_login),
        url(r'^verify/$', TemplateView.as_view(template_name='candidate/verify.html')),
        url(r'^callback/$', handle_candidate_callback),
        url(r'^questionnaire/$', is_authenticated(CandidateQuestionnaireView.as_view())),
        url(r'^dashboard/$', is_authenticated(CandidateDashboardView.as_view())),
        url(r'^submit/$', is_authenticated(CandidateSubmitView.as_view())),
        url(r'^success/$', is_authenticated(TemplateView.as_view(template_name='candidate/success.html'))),
    ])),
    url(r'^groups/nominations/initiatives/', include([
        url(r'^new/$', is_authenticated(CreateInitiativeView.as_view())),
        url(r'^success/$', is_authenticated(TemplateView.as_view(template_name='success.html'))),
    ])),
]
