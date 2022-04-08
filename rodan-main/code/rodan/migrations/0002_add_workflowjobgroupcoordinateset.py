# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('rodan', '0001_rodan_1_0_0_alpha_20160114'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkflowJobGroupCoordinateSet',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('data', jsonfield.fields.JSONField(default={}, null=True, blank=True)),
                ('user_agent', models.CharField(db_index=True, max_length=255, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('workflow_job_group', models.ForeignKey(related_name='workflow_job_group_coordinate_sets', to='rodan.WorkflowJobGroup')),
            ],
            options={
                'permissions': (('view_workflowjobgroupcoordinateset', 'View WorkflowJobGroupCoordinateSet'),),
            },
        ),
        migrations.AlterUniqueTogether(
            name='workflowjobgroupcoordinateset',
            unique_together=set([('user_agent', 'workflow_job_group')]),
        ),
    ]
