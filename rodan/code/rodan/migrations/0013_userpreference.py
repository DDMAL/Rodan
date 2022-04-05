# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rodan', '0012_auto_20160819_1320'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPreference',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('send_email', models.BooleanField(default=True, db_index=True)),
                ('user', models.OneToOneField(related_name='user_preference', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('view_userpreference', 'View User Preference'),),
            },
        ),
    ]
