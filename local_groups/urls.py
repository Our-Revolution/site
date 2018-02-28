from django.conf import settings
from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from .forms import GroupLoginForm
from .views import (
    EventCreateView,
    GroupDashboardView,
    GroupManageView,
    SlackInviteView,
    VerifyEmailRequestView,
    VerifyEmailConfirmView
)

urlpatterns = [
    url(r'^join-us-on-slack', SlackInviteView.as_view())
]

if settings.BSD_LOGIN_ENABLED:
    urlpatterns += [
        url(r'^organizing-hub/', include([
            url(
                r'^$',
                GroupDashboardView.as_view(),
                name='groups-dashboard'
            ),
            url(r'^event/', include([
                url(
                    r'^create/',
                    EventCreateView.as_view(),
                    name='groups-event-create'
                ),
            ])),
            url(
                r'^login/',
                auth_views.login,
                {
                    'authentication_form': GroupLoginForm,
                    'redirect_authenticated_user': True
                },
                name='groups-login'
            ),
            url(
                r'^logout/',
                auth_views.logout,
                {'next_page': 'groups-login'},
                name='groups-logout'
            ),
            url(r'^verify-email/', include([
                url(
                    r"^confirm/(?P<key>[-:\w]+)/$",
                    VerifyEmailConfirmView.as_view(),
                    name="groups-verify-email-confirm"
                ),
                url(
                    r'^request/',
                    VerifyEmailRequestView.as_view(),
                    name='groups-verify-email-request',
                ),
            ])),
            url(r'^(?P<slug>[\w-]+)/', include([
                url(
                    r'^manage/',
                    GroupManageView.as_view(),
                    name='groups-manage'
                ),
            ]))
        ]))
    ]
