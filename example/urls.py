from django.conf.urls import patterns, include
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^concepts/', include('concepts.urls')),
    (r'^admin/', include(admin.site.urls)),
)

urlpatterns = urlpatterns + patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT}),
) if settings.DEBUG else urlpatterns
