from django.conf import settings
from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from .forms import GroupLoginForm
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
            url(r'^(?P<slug>[\w-]+)/', include([
                url(
                    r'^manage',
                    GroupUpdateView.as_view(),
                    name='groups-manage'
                ),
            ]))
        ]))
    ]
