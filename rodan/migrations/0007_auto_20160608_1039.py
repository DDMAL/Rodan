# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rodan', '0006_auto_20160607_1454'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourcelist',
            name='project',
            field=models.ForeignKey(related_name='resourcelists', blank=True, to='rodan.Project', null=True),
        ),
    ]
