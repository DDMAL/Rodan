# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rodan', '0008_tempauthtoken'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tempauthtoken',
            old_name='user_id',
            new_name='user',
        ),
    ]
