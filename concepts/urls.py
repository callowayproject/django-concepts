from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^list$', 'concepts.views.list_tags', name='concepts-autocomplete-list'),
)
