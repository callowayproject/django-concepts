from django import template
from django.core.exceptions import FieldError

from concepts.models import ConceptItem, Concept
from django.contrib.contenttypes.models import ContentType

register = template.Library()


class ConceptsNode(template.Node):
    """
    Sets a context variable to the concepts linked to the object
    """
    def __init__(self, obj, variable_name):
        self.obj = template.Variable(obj)
        self.variable_name = variable_name

    def render(self, context):
        obj = self.obj.resolve(context)
        ctype = ContentType.objects.get_for_model(obj)
        links = ConceptItem.objects.filter(object_id=obj.pk, content_type=ctype)
        context[self.variable_name] = links
        return ''

@register.tag
def get_concepts_for_object(parser, token):
    """
    Get the concepts linked to the object instance passed

    {% get_concepts_for_object object as var %}
    """
    bits = token.split_contents()

    if len(bits) != 4:
        raise template.TemplateSyntaxError("The proper usage is: {%% get_concepts_for_object object as var %}")

    return ConceptsNode(bits[1], bits[3])

@register.filter(name='li_class')
def li_class(weight):
    return 5 - (weight / 5)
