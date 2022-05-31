# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rodan', '0004_auto_20160606_0930'),
    ]

    operations = [
        migrations.AddField(
            model_name='resourcelist',
            name='creator',
            field=models.ForeignKey(related_name='resourcelists', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
