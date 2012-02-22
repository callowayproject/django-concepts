import django
from django.contrib import admin
from django.db.models import Count
from django import forms
from concepts.models import Concept, ConceptItem


class ConceptAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ConceptAdminForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        if instance is not None:
            sub_field = self.fields['substitute']
            sub_field.queryset = sub_field.queryset.exclude(id=instance.id)
    
    class Meta:
        model = Concept

class ConceptItemInline(admin.StackedInline):
    model = ConceptItem

class ConceptAdmin(admin.ModelAdmin):
    list_display = ["name_with_sub", "last_tagged", "items"]
    form = ConceptAdminForm
    raw_id_fields = ('substitute', )
    fieldsets = (
        (None, {'fields': ('name',)}),
        ('Moderation', {
            'fields': ('substitute', 'enabled')
        }),
        ('Geolocation', {
            'classes': ('collapse',),
            'fields': ('woeid', ('longitude', 'latitude'), 
                      ('bbox_w', 'bbox_n'), ('bbox_e', 'bbox_s'),)
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('slug',)
        })
    )
    def items(self, obj):
        return obj.items
    
    def queryset(self, request):
        """
        Return the normal queryset, but add the count of tagged items to it
        """
        if django.VERSION < (1, 2):
            return super(ConceptAdmin, self).queryset(request).annotate(items=Count('conceptitem_items'))
        else:
            return super(ConceptAdmin, self).queryset(request).annotate(items=Count('concepts_conceptitem_items'))

admin.site.register(Concept, ConceptAdmin)
