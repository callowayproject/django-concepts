from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic.list_detail import object_list
from django.utils import simplejson

from concepts.models import ConceptItem, Concept


def tagged_object_list(request, slug, queryset, **kwargs):
    if callable(queryset):
        queryset = queryset()
    tag = get_object_or_404(Concept, slug=slug)
    qs = queryset.filter(pk__in=ConceptItem.objects.filter(
        concept=tag, content_type=ContentType.objects.get_for_model(queryset.model)
    ).values_list("object_id", flat=True))
    if "extra_context" not in kwargs:
        kwargs["extra_context"] = {}
    kwargs["extra_context"]["tag"] = tag
    return object_list(request, qs, **kwargs)


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
    
    return HttpResponse(simplejson.dumps(list(tags)), mimetype='application/javascript')
