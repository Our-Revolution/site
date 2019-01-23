from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from .views import (
    CreateApplicationView,
    NominationsIndexView,
    EditNominationView,
    logout,
    DashboardView,
    CandidateDashboardView,
    ApplicationView,
    EditQuestionnaireView,
    QuestionnaireIndexView,
    CandidateQuestionnaireView,
    CandidateSubmitView,
    handle_candidate_callback,
    candidate_login,
    ApplicationTypeView,
    CreateInitiativeView,
    reset_questionnaire,
)
from django.views.generic import TemplateView
from .decorators import is_authenticated_candidate

urlpatterns = [
    url(r'^groups/nominations/', include([

        # Local Group facing pages
        url(
            r'^$',
            NominationsIndexView.as_view(),
            name='nominations-index'
        ),
        url(
            r'^application/$',
            ApplicationView.as_view(),
            name='nominations-application'
        ),
        url(
            r'^application-type/$',
            ApplicationTypeView.as_view(),
            name='nominations-application-type',
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
        url(r'^logout/$', logout),
        url(
            r'^new/$',
            CreateApplicationView.as_view(),
            name='nominations-application-create',
        ),
        url(r'^nomination/$', EditNominationView.as_view()),
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
            url(r'^callback/$', handle_candidate_callback),
            url(
                r'^dashboard/$',
                is_authenticated_candidate(CandidateDashboardView.as_view())
            ),
            url(r'^login/$', candidate_login),
            url(
                r'^questionnaire/$',
                is_authenticated_candidate(
                    CandidateQuestionnaireView.as_view()
                )
            ),
            url(
                r'^submit/$',
                is_authenticated_candidate(CandidateSubmitView.as_view())
            ),
            url(
                r'^success/$',
                is_authenticated_candidate(TemplateView.as_view(
                    template_name='candidate/success.html'
                ))
            ),
            url(
                r'^verify/$',
                TemplateView.as_view(template_name='candidate/verify.html')
            ),
        ])),
    ])),
]
