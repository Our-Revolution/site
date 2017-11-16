from django.conf.urls import url, include
from django.contrib.auth import views as auth_views


urlpatterns = [
    url(r'^login/', auth_views.login),
    url('^', include('django.contrib.auth.urls')),
]