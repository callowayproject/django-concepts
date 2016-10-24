import django
from django.contrib import admin
from django.contrib.contenttypes.generic import GenericTabularInline
from django.db.models import Count
from django import forms

from concepts.models import Concept, ConceptItem
from concepts.settings import WEIGHTS, WIDGET_CSS_PATH


class ConceptAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ConceptAdminForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        if instance is not None:
            sub_field = self.fields['substitute']
            sub_field.queryset = sub_field.queryset.exclude(id=instance.id)

    class Meta:
        model = Concept
        fields = '__all__'


class ConceptItemAdminForm(forms.ModelForm):
    weight = forms.ChoiceField(label="weighting", choices=WEIGHTS, widget=forms.RadioSelect())

    class Media:
        css = {
            'all': (WIDGET_CSS_PATH,)
        }

    class Meta:
        model = ConceptItem
        fields = '__all__'


class ConceptItemInline(GenericTabularInline):
    form = ConceptItemAdminForm
    model = ConceptItem
    raw_id_fields = ('tag', )

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     return super(ConceptItemInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class ConceptAdmin(admin.ModelAdmin):
    list_display = ["name_with_sub", "last_tagged", "concept_items"]
    form = ConceptAdminForm
    raw_id_fields = ('substitute', )
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ['name']
    fieldsets = (
        (None, {'fields': ('name', 'url',)}),
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

    def concept_items(self, obj):
        return obj.items

    def queryset(self, request):
        """
        Return the normal queryset, but add the count of tagged items to it
        """
        if django.VERSION < (1, 2):
            return super(ConceptAdmin, self).queryset(request).annotate(concept_items=Count('conceptitem_items'))
        else:
            return super(ConceptAdmin, self).queryset(request).annotate(concept_items=Count('concepts_conceptitem_items'))

admin.site.register(Concept, ConceptAdmin)
