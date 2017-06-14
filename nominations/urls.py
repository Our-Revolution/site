from django.conf.urls import url
from .views import CreateApplicationView, NominationsIndexView, EditNominationView

urlpatterns = [
    url(r'^groups/nominations/new', CreateApplicationView.as_view()),
    url(r'^groups/nominations/started', EditNominationView.as_view()),
    url(r'^groups/nominations', NominationsIndexView.as_view()),
]
