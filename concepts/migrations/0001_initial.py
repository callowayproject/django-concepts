# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Concept',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100, verbose_name='Name')),
                ('slug', models.SlugField(unique=True, max_length=100, verbose_name='Slug')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('last_tagged', models.DateTimeField(db_index=True, verbose_name='last time tagged', null=True, editable=False, blank=True)),
                ('enabled', models.BooleanField(default=True, help_text='If unchecked, it will remove current associations and\n            will not allow new associations.', verbose_name='Enabled')),
                ('url', models.CharField(help_text='A URL for more information regarding this concept.', max_length=255, blank=True)),
                ('woeid', models.IntegerField(null=True, verbose_name='where on earth id', blank=True)),
                ('latitude', models.DecimalField(null=True, verbose_name='latitude', max_digits=11, decimal_places=6, blank=True)),
                ('longitude', models.DecimalField(null=True, verbose_name='longitude', max_digits=11, decimal_places=6, blank=True)),
                ('bbox_n', models.DecimalField(null=True, verbose_name='bounding box north', max_digits=11, decimal_places=6, blank=True)),
                ('bbox_s', models.DecimalField(null=True, verbose_name='bounding box south', max_digits=11, decimal_places=6, blank=True)),
                ('bbox_e', models.DecimalField(null=True, verbose_name='bounding box east', max_digits=11, decimal_places=6, blank=True)),
                ('bbox_w', models.DecimalField(null=True, verbose_name='bounding box west', max_digits=11, decimal_places=6, blank=True)),
                ('substitute', models.ForeignKey(blank=True, to='concepts.Concept', help_text='Tag to use instead of this one. Moves current\n            associations to the substitute tag and new association attempts\n            are automatically swapped.', null=True, verbose_name='substitute')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'Concept',
                'verbose_name_plural': 'Concepts',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConceptItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.IntegerField(verbose_name='Object id', db_index=True)),
                ('added', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('weight', models.IntegerField(null=True, blank=True)),
                ('content_type', models.ForeignKey(related_name='concepts_conceptitem_tagged_items', verbose_name='Content type', to='contenttypes.ContentType')),
                ('tag', models.ForeignKey(related_name='concepts_conceptitem_items', to='concepts.Concept')),
            ],
            options={
                'ordering': ('id',),
                'verbose_name': 'Concept Item',
                'verbose_name_plural': 'Concept Items',
            },
            bases=(models.Model,),
        ),
    ]
