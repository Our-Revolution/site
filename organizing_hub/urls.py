from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from local_groups.forms import GroupLoginForm, GroupPasswordResetRequestForm
from local_groups.views import (
    EventCreateView,
    GroupManageView,
    GroupPasswordChangeView,
    GroupPasswordResetView,
    SlackInviteView,
    VerifyEmailRequestView,
    VerifyEmailConfirmView
)
from .views import GroupAdminsView

urlpatterns = [
    url(r'^join-us-on-slack', SlackInviteView.as_view())
]

urlpatterns += [
    url(r'^organizing-hub/', include([
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
        url(r'^password/', include([
            url(
                r'^change/',
                GroupPasswordChangeView.as_view(),
                name='groups-password-change',
            ),
            url(r'^reset/', include([
                url(
                    r'^$',
                    auth_views.password_reset,
                    {'password_reset_form': GroupPasswordResetRequestForm},
                    name='password_reset',
                ),
                url(
                    r'^confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                    GroupPasswordResetView.as_view(),
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
                r'^admins/',
                GroupAdminsView.as_view(),
                name='organizing-hub-group-admins'
            ),
            url(
                r'^info/',
                GroupManageView.as_view(),
                name='groups-manage'
            ),
        ]))
    ]))
]