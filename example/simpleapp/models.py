from django.db import models

from concepts.managers import ConceptManager
from concepts.models import ConceptItem
from django.contrib.contenttypes.fields import GenericRelation


class SimpleText(models.Model):
    """
    (SimpleText description)
    """

    name        = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created     = models.DateTimeField(auto_now_add=True)
    updated     = models.DateTimeField(auto_now=True)
    concepts = ConceptManager(blank=True)

    class Meta:
        verbose_name_plural = 'Simple Text'
        ordering = ('-created',)
        get_latest_by = 'updated'

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('simpletext_detail_view_name', [str(self.id)])


class SimpleTextTwo(models.Model):
    """
    (SimpleText description)
    """

    name        = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created     = models.DateTimeField(auto_now_add=True)
    updated     = models.DateTimeField(auto_now=True)
    concept_items = GenericRelation(ConceptItem)

    class Meta:
        verbose_name_plural = 'Simple Text'
        ordering = ('-created',)
        get_latest_by = 'updated'

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('simpletext_detail_view_name', [str(self.id)])
