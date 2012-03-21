import datetime

import django
from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext

from taggit.models import TagBase, GenericTaggedItemBase, ItemBase

class Concept(TagBase):
    """An idea or other freeform categorization of something"""
    
    created = models.DateTimeField(_('created'), 
        auto_now_add=True,
        editable=False)
    last_tagged = models.DateTimeField(_('last time tagged'), 
        blank=True, null=True, editable=False, db_index=True)
    substitute = models.ForeignKey('Concept', 
        blank=True, null=True, verbose_name=_('substitute'),
        help_text=_("""Tag to use instead of this one. Moves current 
            associations to the substitute tag and new association attempts
            are automatically swapped."""))
    enabled = models.BooleanField(_("Enabled"), default=True, 
        help_text=_("""If unchecked, it will remove current associations and
            will not allow new associations."""))
    url = models.CharField(blank=True, max_length=255, 
        help_text=_("A URL for more information regarding this concept."))
    woeid = models.IntegerField(_('where on earth id'), blank=True, null=True)
    latitude = models.DecimalField(_('latitude'), 
        max_digits=11, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(_('longitude'),
        max_digits=11, decimal_places=6, blank=True, null=True)
    bbox_n = models.DecimalField(_('bounding box north'), 
        max_digits=11, decimal_places=6, blank=True, null=True)
    bbox_s = models.DecimalField(_('bounding box south'), 
        max_digits=11, decimal_places=6, blank=True, null=True)
    bbox_e = models.DecimalField(_('bounding box east'), 
        max_digits=11, decimal_places=6, blank=True, null=True)
    bbox_w = models.DecimalField(_('bounding box west'), 
        max_digits=11, decimal_places=6, blank=True, null=True)
    
    @property
    def items(self):
        if django.VERSION < (1, 2):
            return self.conceptitem_items
        else:
            return self.concepts_conceptitem_items
    
    def name_with_sub(self):
        """
        Render the name, or name with indication what its substitute is
        """
        if self.substitute:
            return "%s &rarr; %s" % (self.name, self.substitute)
        elif not self.enabled:
            return '<span style="text-decoration: line-through">%s</span>' % self.name
        else:
            return self.name
    name_with_sub.short_description = _("Name")
    name_with_sub.admin_order_field = "name"
    name_with_sub.allow_tags = True
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.datetime.today()
        super(Concept, self).save(*args, **kwargs)
        if self.substitute:
            items = self.items.all()
            items.update(tag=self.substitute)
        if not self.enabled:
            self.items.all().delete()
    
    class Meta:
        verbose_name = _("Concept")
        verbose_name_plural = _("Concepts")
        ordering = ("name",)


class ConceptItemBase(ItemBase):
    if django.VERSION < (1, 2):
        tag = models.ForeignKey(Concept, related_name="%(class)s_items")
    else:
        tag = models.ForeignKey(Concept, related_name="%(app_label)s_%(class)s_items")

    class Meta:
        abstract = True
    
    @classmethod
    def tags_for(cls, model, instance=None):
        if instance is not None:
            return cls.tag_model().objects.filter(**{
                '%s__content_object' % cls.tag_relname(): instance
            })
        return cls.tag_model().objects.filter(**{
            '%s__content_object__isnull' % cls.tag_relname(): False
        }).distinct()

class ConceptItem(GenericTaggedItemBase, ConceptItemBase):
    added = models.DateTimeField(auto_now_add=True, db_index=True)
    weight = models.IntegerField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        """
        Add the date added and last_tagged to Tag
        """
        if not self.added:
            self.added = datetime.datetime.now()
        
        super(ConceptItem, self).save(*args, **kwargs)
        self.tag.last_tagged = self.added
        self.tag.save()
    
    class Meta:
        verbose_name = _("Concept Item")
        verbose_name_plural = _("Concept Items")
        ordering = ('id',)
