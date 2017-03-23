from django.conf.urls import url
from .views import SlackInviteView

urlpatterns = [
    url(r'^join-us-on-slack', SlackInviteView.as_view())
]