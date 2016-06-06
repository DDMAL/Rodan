# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import sortedm2m.fields


class Migration(migrations.Migration):

    dependencies = [
        ('rodan', '0003_add_resourcelist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourcelist',
            name='resources',
            field=sortedm2m.fields.SortedManyToManyField(help_text=None, to='rodan.Resource', null=True, blank=True),
        ),
    ]
