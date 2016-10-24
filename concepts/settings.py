from django.conf import settings
from django.utils.translation import ugettext_lazy as _

DEFAULT_SETTINGS = {
    'PARSER': 'concepts.parsers.default',
    'WIDGET': 'concepts.widgets.TextExtWidget',
    'WEIGHTS': ((0, 'Hide'), (10, 'Low'), (20, 'Medium'), (30, 'High')),
    'WIDGET_CSS_PATH': 'concepts/horizontalradio.css',
    'CATEGORY_CHOICES': [
        ('concept', _('Concept')),
        ('date', _('Date, (Holiday, Event)')),
        ('term', _('Industry Term')),
        ('location', _('Location')),
        ('natural-feature', _('Natural Feature')),
        ('organism', _('Organism (Animal, Plant)')),
        ('organization', _('Organization')),
        ('person', _('Person')),
    ],
}

USER_SETTINGS = DEFAULT_SETTINGS.copy()
USER_SETTINGS.update(getattr(settings, 'CONCEPTS_SETTINGS', {}))

if callable(USER_SETTINGS['PARSER']):
    pass
elif isinstance(USER_SETTINGS['PARSER'], basestring):
    from django.utils.importlib import import_module
    bits = USER_SETTINGS['PARSER'].split(".")
    module = import_module(".".join(bits[:-1]))
    USER_SETTINGS['PARSER'] = getattr(module, bits[-1])
else:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured("PARSER must be a callable or a string.")

if isinstance(USER_SETTINGS['WIDGET'], basestring):
    from django.utils.importlib import import_module
    bits = USER_SETTINGS['WIDGET'].split(".")
    module = import_module(".".join(bits[:-1]))
    USER_SETTINGS['WIDGET'] = getattr(module, bits[-1])
else:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured("WIDGET must be a string.")

globals().update(USER_SETTINGS)
