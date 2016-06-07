# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rodan', '0006_auto_20160607_1454'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resource',
            name='compat_resource_file',
        ),
    ]
