from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.views.i18n import javascript_catalog

from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtaildocs import urls as wagtaildocs_urls
from wagtail.wagtailcore import urls as wagtail_urls

import documents


urlpatterns = []

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns += [
#         url(r'^__debug__/', include(debug_toolbar.urls)),
#     ]

urlpatterns += [
     # override default wagtail view
    url(r'^documents/(\d+)/(.*)$', documents.serve_wagtail_doc,
        name='wagtaildocs_serve'),
    url(r'^cms/', include(wagtailadmin_urls)),
    url(r'^admin/', admin.site.urls),
    url(r'', include('bsd.urls')),
    url(r'', include('local_groups.urls')),
    url(r'', include('nominations.urls')),
    url(r'', include(wagtail_urls))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# django-recurrence hack
js_info_dict = {
    'packages': ('recurrence', )
}

urlpatterns += [
    url(r'^jsi18n/$', javascript_catalog, js_info_dict)
]
