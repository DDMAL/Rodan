# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rodan', '0008_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resource',
            name='has_thumb',
        ),
    ]
