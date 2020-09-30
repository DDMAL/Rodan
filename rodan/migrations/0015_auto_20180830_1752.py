# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rodan', '0014_auto_20161019_1307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inputport',
            name='input_port_type',
            field=models.ForeignKey(to='rodan.InputPortType'),
        ),
        migrations.AlterField(
            model_name='outputport',
            name='output_port_type',
            field=models.ForeignKey(to='rodan.OutputPortType'),
        ),
    ]
