from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import patterns, include, url
from shared.views import home

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', home, name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG and settings.MEDIA_ROOT:
    urlpatterns += static(settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT)
if settings.DEBUG and settings.STATIC_ROOT:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

