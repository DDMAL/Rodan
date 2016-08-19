# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('rodan', '0011_auto_20160816_1222'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tempauthtoken',
            name='user',
            field=models.OneToOneField(related_name='temp_authtoken', to=settings.AUTH_USER_MODEL),
        ),
    ]
