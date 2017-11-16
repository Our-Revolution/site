from django.conf import settings
from django.conf.urls import url, include
from django.contrib.auth import views as auth_views


urlpatterns = []

if settings.BSD_LOGIN_ENABLED:
    urlpatterns += [
        url(r'^login/', auth_views.login),
        url('^', include('django.contrib.auth.urls')),
    ]
