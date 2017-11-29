from django.conf.urls import include, url
from .views import GroupUpdateView, SlackInviteView

urlpatterns = [
    url(r'^groups/(?P<slug>[\w-]+)/', include([
        url(r'^update', GroupUpdateView.as_view()),
    ])),
    url(r'^join-us-on-slack', SlackInviteView.as_view())
]
