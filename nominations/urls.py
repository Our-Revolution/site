from django.conf.urls import include, url
from .views import CreateApplicationView, NominationsIndexView, EditNominationView, handle_auth0_callback, logout, login, DashboardView, ApplicationView
from django.views.generic import TemplateView
from .decorators import is_authenticated

# placeholder urls to code templates
urlpatterns = [
    url(r'^groups/nominations/', include([
        url(r'^dashboard/$', is_authenticated(DashboardView.as_view())),
        url(r'^login/$', login),
        url(r'^logout/$', is_authenticated(logout)),
        url(r'^callback/$', handle_auth0_callback),
        url(r'^verify/$', TemplateView.as_view(template_name='verify.html')),
        url(r'^application/$', is_authenticated(ApplicationView.as_view())),
        url(r'^questionnaire/$', is_authenticated(TemplateView.as_view(template_name='questionnaire_index.html'))),
        url(r'^new/$', is_authenticated(CreateApplicationView.as_view())),
        url(r'^nomination/$', EditNominationView.as_view()),
        url(r'^$', NominationsIndexView.as_view()),
    ])),
]
