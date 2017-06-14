from django.conf.urls import url
from .views import CreateApplicationView, NominationsIndexView, EditNominationView
from django.views.generic import TemplateView

# placeholder urls to code templates
urlpatterns = [
    url(r'^groups/nominations/status', TemplateView.as_view(template_name='application_status.html')),
    url(r'^groups/nominations/questionnaire', TemplateView.as_view(template_name='questionnaire_index.html')),
    url(r'^groups/nominations/new', CreateApplicationView.as_view()),
    url(r'^groups/nominations/nomination', EditNominationView.as_view()),
    url(r'^groups/nominations', NominationsIndexView.as_view()),
]
