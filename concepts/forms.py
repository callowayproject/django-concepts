from django import forms
from .settings import WIDGET

class ConceptField(forms.CharField):
    widget = WIDGET
    
    def __init__(self, *args, **kwargs):
        if 'parser' in kwargs:
            if not callable(kwargs['parser']):
                raise ImproperlyConfigured(_("The 'parser' provided must be a callable."))
            
            self.parser = kwargs['parser']
            del(kwargs['parser'])
        else:
            self.parser = parse_tags
        super(ConceptField, self).__init__(*args, **kwargs)
    
    def clean(self, value):
        if isinstance(value, (list, tuple)):
            return list(set(value))
        value = super(ConceptField, self).clean(value)
        try:
            return self.parser(value)
        except ValueError:
            raise forms.ValidationError(_("Please provide a list of concepts."))
