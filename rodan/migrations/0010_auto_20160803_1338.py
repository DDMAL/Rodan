# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('rodan', '0009_auto_20160803_1255'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tempauthtoken',
            name='user',
            field=models.ForeignKey(related_name='temp_authtoken', to=settings.AUTH_USER_MODEL, unique=True),
        ),
    ]
