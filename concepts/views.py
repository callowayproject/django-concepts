from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
import json

from concepts.models import ConceptItem, Concept


class ExtraContextListView(ListView):
    extra_context = {}

    def get_context_data(self, **kwargs):
        context = super(ExtraContextListView, self).get_context_data(**kwargs)
        context.update(self.extra_context)
        return context


def tagged_object_list(request, slug, queryset, **kwargs):
    """
    A thin wrapper around
    ``django.views.generic.list_detail.object_list`` which creates a
    ``QuerySet`` containing instances of the given queryset or model
    tagged with the given tag.

    In addition to the context variables set up by ``object_list``, a
    ``tag`` context variable will contain the ``Tag`` instance for the
    tag.
    """
    if callable(queryset):
        queryset = queryset()
    tag = get_object_or_404(Concept, slug=slug)
    ctype = ContentType.objects.get_for_model(queryset.model)
    pks = ConceptItem.objects.filter(tag=tag, content_type=ctype).values_list("object_id", flat=True)
    qs = queryset.filter(pk__in=pks)
    if "extra_context" not in kwargs:
        kwargs["extra_context"] = {}
    kwargs["extra_context"]["tag"] = tag
    return ExtraContextListView.as_view(queryset=qs, **kwargs)(request)


def list_tags(request):
    term = request.GET.get('term', '')
    if not term:
        term = request.GET.get('q', '')
    if term:
        tag_items = Concept.objects.filter(name__istartswith=term).values_list(
            'name', 'substitute__name', 'enabled')
        tags = []
        for item in tag_items:
            if item[1]:
                tags.append("%s|%s" % (item[0], item[1]))
            elif not item[2]:
                tags.append("%s|-" % item[0])
            else:
                tags.append(item[0])
    else:
        tags = []

    return HttpResponse(json.dumps(list(tags)), content_type='application/javascript')
