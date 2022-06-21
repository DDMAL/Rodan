# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rodan', '0007_auto_20160620_1153'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tempauthtoken',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('expiry', models.DateTimeField(null=True, db_index=True)),
                ('user_id', models.ForeignKey(related_name='temp_authtoken', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('view_tempauthtoken', 'View Temp Authtoken'),),
            },
        ),
    ]
