from django.conf.urls import url
from .views import NominationsIndexView, NewApplicationView

urlpatterns = [
    url(r'^groups/nominations/new', NewApplicationView.as_view()),
    url(r'^groups/nominations', NominationsIndexView.as_view()),
]
