from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.utils.text import capfirst

from taggit.managers import TaggableManager, _get_subclasses

from .models import ConceptItem
from .forms import ConceptField
from .settings import PARSER


class ConceptManager(TaggableManager):
    def __init__(self, verbose_name=_("Concepts"), help_text=_("Press return to complete each tag."), through=ConceptItem, **kwargs):
        super(ConceptManager, self).__init__(verbose_name, help_text, through, **kwargs)

    def extra_filters(self, pieces, pos, negate):
        if negate or not self.use_gfk:
            return []
        prefix = "__".join(["concept_items"] + pieces[:pos - 2])
        cts = map(ContentType.objects.get_for_model, _get_subclasses(self.model))
        if len(cts) == 1:
            return [("%s__content_type" % prefix, cts[0])]
        return [("%s__content_type__in" % prefix, cts)]

    def formfield(self, form_class=ConceptField, **kwargs):
        defaults = {
            "label": capfirst(self.verbose_name),
            "help_text": self.help_text,
            "required": not self.blank,
            "parser": PARSER,
        }
        defaults.update(kwargs)
        return form_class(**defaults)
