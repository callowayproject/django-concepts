import datetime

import django
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.db import connection, models
qn = connection.ops.quote_name

from taggit.models import TagBase, GenericTaggedItemBase, ItemBase
from .settings import CATEGORY_CHOICES


def get_queryset_and_model(queryset_or_model):
    """
    Given a ``QuerySet`` or a ``Model``, returns a two-tuple of
    (queryset, model).

    If a ``Model`` is given, the ``QuerySet`` returned will be created
    using its default manager.
    """
    try:
        return queryset_or_model, queryset_or_model.model
    except AttributeError:
        return queryset_or_model._default_manager.all(), queryset_or_model


class ConceptModelManager(models.Manager):
    def get_intersection_by_model(self, queryset_or_model, tags):
        """
        Create a ``QuerySet`` containing instances of the specified
        model associated with *all* of the given list of tags.
        """
        tag_count = len(tags)
        queryset, model = get_queryset_and_model(queryset_or_model)

        if not tag_count:
            return model._default_manager.none()

        model_table = qn(model._meta.db_table)
        # This query selects the ids of all objects which have all the
        # given tags.
        query = """
        SELECT %(model_pk)s
        FROM %(model)s, %(tagged_item)s
        WHERE %(tagged_item)s.content_type_id = %(content_type_id)s
          AND %(tagged_item)s.tag_id IN (%(tag_id_placeholders)s)
          AND %(model_pk)s = %(tagged_item)s.object_id
        GROUP BY %(model_pk)s
        HAVING COUNT(%(model_pk)s) = %(tag_count)s""" % {
            'model_pk': '%s.%s' % (model_table, qn(model._meta.pk.column)),
            'model': model_table,
            'tagged_item': qn(self.model._meta.db_table),
            'content_type_id': ContentType.objects.get_for_model(model).pk,
            'tag_id_placeholders': ','.join(['%s'] * tag_count),
            'tag_count': tag_count,
        }

        cursor = connection.cursor()
        cursor.execute(query, [tag.pk for tag in tags])
        object_ids = [row[0] for row in cursor.fetchall()]
        if len(object_ids) > 0:
            return queryset.filter(pk__in=object_ids)
        else:
            return model._default_manager.none()

    def get_union_by_model(self, queryset_or_model, tags):
        """
        Create a ``QuerySet`` containing instances of the specified
        model associated with *any* of the given list of tags.
        """
        tag_count = len(tags)
        queryset, model = get_queryset_and_model(queryset_or_model)

        if not tag_count:
            return model._default_manager.none()

        model_table = qn(model._meta.db_table)
        # This query selects the ids of all objects which have any of
        # the given tags.
        query = """
        SELECT %(model_pk)s
        FROM %(model)s, %(tagged_item)s
        WHERE %(tagged_item)s.content_type_id = %(content_type_id)s
          AND %(tagged_item)s.tag_id IN (%(tag_id_placeholders)s)
          AND %(model_pk)s = %(tagged_item)s.object_id
        GROUP BY %(model_pk)s""" % {
            'model_pk': '%s.%s' % (model_table, qn(model._meta.pk.column)),
            'model': model_table,
            'tagged_item': qn(self.model._meta.db_table),
            'content_type_id': ContentType.objects.get_for_model(model).pk,
            'tag_id_placeholders': ','.join(['%s'] * tag_count),
        }

        cursor = connection.cursor()
        cursor.execute(query, [tag.pk for tag in tags])
        object_ids = [row[0] for row in cursor.fetchall()]
        if len(object_ids) > 0:
            return queryset.filter(pk__in=object_ids)
        else:
            return model._default_manager.none()

    def _get_usage(self, model, counts=False, min_count=None, extra_joins=None, extra_criteria=None, params=None):
        """
        Perform the custom SQL query for ``usage_for_model`` and
        ``usage_for_queryset``.
        """
        if min_count is not None:
            counts = True

        model_table = qn(model._meta.db_table)
        model_pk = '%s.%s' % (model_table, qn(model._meta.pk.column))
        query = """
        SELECT DISTINCT %(tag)s.id, %(tag)s.name%(count_sql)s
        FROM
            %(tag)s
            INNER JOIN %(tagged_item)s
                ON %(tag)s.id = %(tagged_item)s.tag_id
            INNER JOIN %(model)s
                ON %(tagged_item)s.object_id = %(model_pk)s
            %%s
        WHERE %(tagged_item)s.content_type_id = %(content_type_id)s
            %%s
        GROUP BY %(tag)s.id, %(tag)s.name
        %%s
        ORDER BY %(tag)s.name ASC""" % {
            'tag': qn(self.model._meta.db_table),
            'count_sql': counts and (', COUNT(%s)' % model_pk) or '',
            'tagged_item': qn(ConceptItem._meta.db_table),
            'model': model_table,
            'model_pk': model_pk,
            'content_type_id': ContentType.objects.get_for_model(model).pk,
        }

        min_count_sql = ''
        if min_count is not None:
            min_count_sql = 'HAVING COUNT(%s) >= %%s' % model_pk
            params.append(min_count)

        cursor = connection.cursor()
        cursor.execute(query % (extra_joins, extra_criteria, min_count_sql), params)
        tags = []
        for row in cursor.fetchall():
            t = self.model(*row[:2])
            if counts:
                t.count = row[2]
            tags.append(t)
        return tags

    def usage_for_model(self, model, counts=False, min_count=None, filters=None):
        """
        Obtain a list of tags associated with instances of the given
        Model class.

        If ``counts`` is True, a ``count`` attribute will be added to
        each tag, indicating how many times it has been used against
        the Model class in question.

        If ``min_count`` is given, only tags which have a ``count``
        greater than or equal to ``min_count`` will be returned.
        Passing a value for ``min_count`` implies ``counts=True``.

        To limit the tags (and counts, if specified) returned to those
        used by a subset of the Model's instances, pass a dictionary
        of field lookups to be applied to the given Model as the
        ``filters`` argument.
        """
        if filters is None:
            filters = {}

        queryset = model._default_manager.filter()
        for f in filters.items():
            queryset.query.add_filter(f)
        usage = self.usage_for_queryset(queryset, counts, min_count)

        return usage

    def usage_for_queryset(self, queryset, counts=False, min_count=None):
        """
        Obtain a list of tags associated with instances of a model
        contained in the given queryset.

        If ``counts`` is True, a ``count`` attribute will be added to
        each tag, indicating how many times it has been used against
        the Model class in question.

        If ``min_count`` is given, only tags which have a ``count``
        greater than or equal to ``min_count`` will be returned.
        Passing a value for ``min_count`` implies ``counts=True``.
        """

        if getattr(queryset.query, 'get_compiler', None):
            # Django 1.2+
            compiler = queryset.query.get_compiler(using='default')
            extra_joins = ' '.join(compiler.get_from_clause()[0][1:])
            where, params = queryset.query.where.as_sql(
                compiler.quote_name_unless_alias, compiler.connection
            )
        else:
            # Django pre-1.2
            extra_joins = ' '.join(queryset.query.get_from_clause()[0][1:])
            where, params = queryset.query.where.as_sql()

        if where:
            extra_criteria = 'AND %s' % where
        else:
            extra_criteria = ''
        return self._get_usage(queryset.model, counts, min_count, extra_joins, extra_criteria, params)


class Concept(TagBase):
    """An idea or other freeform categorization of something"""
    category = models.CharField(
        _('category'),
        max_length=20,
        blank=True, null=True,
        choices=CATEGORY_CHOICES,
        default='concept')
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
    geonamesid = models.IntegerField(_('GeoNames id'), blank=True, null=True)
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
    geometry = models.TextField(
        _('geometry'),
        blank=True, null=True)

    objects = ConceptModelManager()

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
        Concept.objects.filter(id=self.tag.id).update(last_tagged=self.added)
        # self.tag.save()

    class Meta:
        verbose_name = _("Concept Item")
        verbose_name_plural = _("Concept Items")
        ordering = ('id',)


# The association between concepts and a related item must be
# deleted when the item is deleted
def delete_listener(sender, instance, **kwargs):
    ctype = ContentType.objects.get_for_model(sender)
    ConceptItem.objects.filter(content_type=ctype,
                               object_id=instance.id).delete()
