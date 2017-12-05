from django.conf import settings
from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from .views import GroupDashboardView, GroupUpdateView, SlackInviteView

urlpatterns = [
    url(r'^join-us-on-slack', SlackInviteView.as_view())
]

if settings.BSD_LOGIN_ENABLED:
    urlpatterns += [
        url(r'^groups/', include([
            url(
                r'^dashboard/',
                GroupDashboardView.as_view(),
                name='groups-dashboard'
            ),
            url(r'^login/', auth_views.login, name='groups-login'),
            url('^', include('django.contrib.auth.urls')),
            url(r'^(?P<slug>[\w-]+)/', include([
                url(r'^update', GroupUpdateView.as_view()),
            ]))
        ]))
    ]
