from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^list$', 'concepts.views.list_tags', name='concepts-autocomplete-list'),
)
