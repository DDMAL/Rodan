# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import sortedm2m.fields


class Migration(migrations.Migration):

    dependencies = [
        ('rodan', '0015_auto_20180830_1752'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='job_queue',
            field=models.CharField(default=b'celery', max_length=15),
        ),
        migrations.AddField(
            model_name='runjob',
            name='job_queue',
            field=models.CharField(default=b'celery', max_length=15),
        ),
        migrations.AlterField(
            model_name='resourcelist',
            name='resources',
            field=sortedm2m.fields.SortedManyToManyField(help_text=None, to='rodan.Resource', blank=True),
        ),
    ]
