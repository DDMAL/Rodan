# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rodan', '0010_auto_20160803_1338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workflowrun',
            name='status',
            field=models.IntegerField(default=0, db_index=True, choices=[(21, b'Request processing'), (1, b'Processing'), (4, b'Finished'), (-1, b'Failed'), (29, b'Request cancelling'), (9, b'Cancelled'), (31, b'Request retrying'), (11, b'Retrying')]),
        ),
    ]
