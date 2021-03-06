from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from .views import (
    CreateApplicationView,
    NominationsIndexView,
    PrioritySupportView,
    EditNominationView,
    DashboardView,
    CandidateDashboardView,
    ApplicationView,
    EditQuestionnaireView,
    QuestionnaireIndexView,
    QuestionnaireSelectView,
    CandidateQuestionnaireView,
    CandidateQuestionnaireSelectView,
    CandidateSuccessView,
    ApplicationStartView,
    CreateInitiativeView,
    reset_questionnaire,
)
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^groups/nominations/', include([

        # Local Group facing pages
        url(
            r'^$',
            NominationsIndexView.as_view(),
            name='nominations-index'
        ),
        url(r'^application/', include([
            url(
                r'^$',
                ApplicationView.as_view(),
                name='nominations-application'
            ),
            url(r'^(?P<pk>[0-9]+)/', include([
                url(
                    r'^priority-support/$',
                    PrioritySupportView.as_view(),
                    name='nominations-priority-support',
                ),
                url(
                    r'(?:(?P<app_complete>[0-9]+)/)?$',
                    QuestionnaireSelectView.as_view(),
                    name='nominations-questionnaire-select',
                ),
            ])),
        ])),
        url(
            r'^application-start/$',
            ApplicationStartView.as_view(),
            name='nominations-application-start',
        ),
        url(
            r'^dashboard/$',
            DashboardView.as_view(),
            name='nominations-dashboard'
        ),
        url(
            r'^email-success/$',
            login_required(TemplateView.as_view(
                template_name='email-success.html'
            )),
            name='nominations-questionnaire-sent',
        ),
        url(r'^initiatives/', include([
            url(
                r'^new/$',
                CreateInitiativeView.as_view(),
                name='nominations-initiative-create'
            ),
            url(r'^success/$', login_required(TemplateView.as_view(
                template_name='success.html'
            ))),
        ])),
        url(
            r'^new/$',
            CreateApplicationView.as_view(),
            name='nominations-application-create',
        ),
        url(
            r'^nomination/$',
            EditNominationView.as_view(),
            name='nominations-nomination-edit',
        ),
        url(r'^questionnaire/', include([
            url(
                r'^$',
                QuestionnaireIndexView.as_view(),
                name='nominations-questionnaire'
            ),
            url(
                r'^edit$',
                EditQuestionnaireView.as_view(),
                name='nominations-questionnaire-edit'
            ),
            url(
                r'^reset$',
                reset_questionnaire,
                name='nominations-questionnaire-reset'
            ),
        ])),

        # Candidate facing pages
        url(r'^candidate/', include([
            url(
                r'application/(?P<pk>[0-9]+)/(?:(?P<app_complete>[0-9]+)/)?$',
                CandidateQuestionnaireSelectView.as_view(),
                name='nominations-candidate-questionnaire-select',
            ),
            url(
                r'^dashboard/$',
                CandidateDashboardView.as_view(),
                name='nominations-candidate-dashboard',
            ),
            url(
                r'^questionnaire/(?P<app_id>[0-9]+)/$',
                CandidateQuestionnaireView.as_view(),
                name='nominations-candidate-questionnaire',
            ),
            url(
                r'^success/$',
                CandidateSuccessView.as_view(),
                name='nominations-candidate-success',
            ),
        ])),
    ])),
]
