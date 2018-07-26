from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from local_groups.forms import GroupLoginForm, PasswordResetRequestForm
from local_groups.views import (
    GroupManageView,
    SlackInviteView,
    VerifyEmailRequestView,
    VerifyEmailConfirmView,
)
from .views import (
    AccountCreateView,
    EventCreateView,
    EventListView,
    EventPromoteView,
    EventUpdateView,
    GroupAdminsView,
    PasswordChangeView,
    PasswordResetView,
    TaskTestView,
)

urlpatterns = [
    url(r'^join-us-on-slack', SlackInviteView.as_view())
]

urlpatterns += [
    url(r'^organizing-hub/', include([
        url(r'^event/', include([
            url(
                r'^$',
                EventListView.as_view(),
                name='organizing-hub-event-list'
            ),
            url(
                r'^create/',
                EventCreateView.as_view(),
                name='organizing-hub-event-create'
            ),
            url(
                r'^(?P<event_id_obfuscated>[\w-]+)/promote/',
                EventPromoteView.as_view(),
                name='organizing-hub-event-promote'
            ),
            url(
                r'^(?P<event_id_obfuscated>[\w-]+)/update/',
                EventUpdateView.as_view(),
                name='organizing-hub-event-update'
            ),
        ])),
        url(
            r'^login/',
            auth_views.login,
            {
                'authentication_form': GroupLoginForm,
                'redirect_authenticated_user': True
            },
            name='organizing-hub-login'
        ),
        url(
            r'^logout/',
            auth_views.logout,
            {'next_page': 'organizing-hub-login'},
            name='groups-logout'
        ),
        url(r'^account/', include([
            url(
                r'^$',
                PasswordChangeView.as_view(),
                name='groups-password-change',
            ),
            url(
                r'^create/',
                AccountCreateView.as_view(),
                name='organizing-hub-account-create'
            ),
        ])),
        url(r'^password/', include([
            url(r'^reset/', include([
                url(
                    r'^$',
                    auth_views.password_reset,
                    {'password_reset_form': PasswordResetRequestForm},
                    name='password_reset',
                ),
                url(
                    r'^confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                    PasswordResetView.as_view(),
                    name='password_reset_confirm',
                ),
                url(
                    r'^done/',
                    auth_views.password_reset_done,
                    name='password_reset_done',
                ),
            ])),
        ])),
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
                r'^users/',
                GroupAdminsView.as_view(),
                name='organizing-hub-group-admins'
            ),
            url(
                r'^update/',
                GroupManageView.as_view(),
                name='groups-manage'
            ),
        ])),
        url(
            r'^task-test/',
            TaskTestView.as_view(),
        ),
    ]))
]
