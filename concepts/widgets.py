from django import forms
from django.db.models.query import QuerySet
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
import json


class TextExtWidget(forms.TextInput):
    input_type = 'text'

    def render(self, name, value, attrs=None):
        list_view = reverse('concepts-autocomplete-list')
        if value is not None:
            if isinstance(value, QuerySet):
                value = [o.tag.name for o in value.select_related("tag")]
            elif isinstance(value, basestring):
                value = [value]
        else:
            value = []
        html = super(TextExtWidget, self).render(name, '', attrs)
        js = render_to_string('concepts/textext.html', {
            "element_id": attrs['id'],
            "autocomplete_url": list_view,
            "items": json.dumps(list(value))
        })
        return mark_safe("\n".join([html, js]))

    def value_from_datadict(self, data, files, name):
        tags = json.loads(data[name])
        return tags

    class Media:
        css = {'all': ('concepts/textext.css',)}
        js = ('concepts/jquery-textext.js',)
