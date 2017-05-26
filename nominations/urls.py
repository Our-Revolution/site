from django.conf.urls import url
from .views import NominationsIndexView

urlpatterns = [
    url(r'^groups/nominations', NominationsIndexView.as_view()),
    url(r'^groups/nominations/new', NewNominationForm.as_view())
    
]
