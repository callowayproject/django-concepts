# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('concepts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='concept',
            name='category',
            field=models.CharField(default=b'concept', choices=[(b'concept', 'Concept'), (b'date', 'Date, (Holiday, Event)'), (b'term', 'Industry Term'), (b'location', 'Location'), (b'natural-feature', 'Natural Feature'), (b'organism', 'Organism (Animal, Plant)'), (b'organization', 'Organization'), (b'person', 'Person')], max_length=20, blank=True, null=True, verbose_name='category'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='concept',
            name='geometry',
            field=models.TextField(null=True, verbose_name='geometry', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='concept',
            name='geonamesid',
            field=models.IntegerField(null=True, verbose_name='GeoNames id', blank=True),
            preserve_default=True,
        ),
    ]
