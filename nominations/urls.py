from django.conf.urls import url
from .views import NominationsIndexView

urlpatterns = [
    url(r'^groups/nominations', NominationsIndexView.as_view())
]
