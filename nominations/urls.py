from django.conf.urls import url
from .views import GroupNominationsIndexView

urlpatterns = [
    url(r'^groups/nominations', GroupNominationsIndexView.as_view())
]
