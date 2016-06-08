# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import django.db.models.deletion
from django.conf import settings
import rodan.models.resource
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Connection',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
            ],
            options={
                'permissions': (('view_connection', 'View Connection'),),
            },
        ),
        migrations.CreateModel(
            name='Input',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('input_port_type_name', models.CharField(max_length=255, db_index=True)),
            ],
            options={
                'permissions': (('view_input', 'View Input'),),
            },
        ),
        migrations.CreateModel(
            name='InputPort',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('label', models.CharField(db_index=True, max_length=255, null=True, blank=True)),
                ('extern', models.BooleanField(default=False, db_index=True)),
            ],
            options={
                'permissions': (('view_inputport', 'View InputPort'),),
            },
        ),
        migrations.CreateModel(
            name='InputPortType',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('minimum', models.IntegerField(db_index=True)),
                ('maximum', models.IntegerField(db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200, db_index=True)),
                ('author', models.CharField(db_index=True, max_length=255, null=True, blank=True)),
                ('category', models.CharField(db_index=True, max_length=255, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('settings', jsonfield.fields.JSONField(default={b'type': b'object'})),
                ('enabled', models.BooleanField(default=False, db_index=True)),
                ('interactive', models.BooleanField(default=False, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='Output',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('output_port_type_name', models.CharField(max_length=255, db_index=True)),
            ],
            options={
                'permissions': (('view_output', 'View Output'),),
            },
        ),
        migrations.CreateModel(
            name='OutputPort',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('label', models.CharField(db_index=True, max_length=255, null=True, blank=True)),
                ('extern', models.BooleanField(default=False, db_index=True)),
            ],
            options={
                'permissions': (('view_outputport', 'View OutputPort'),),
            },
        ),
        migrations.CreateModel(
            name='OutputPortType',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('minimum', models.IntegerField(db_index=True)),
                ('maximum', models.IntegerField(db_index=True)),
                ('job', models.ForeignKey(related_name='output_port_types', to='rodan.Job')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('description', models.TextField(db_index=True, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('admin_group', models.ForeignKey(related_name='project_as_admin', to='auth.Group')),
                ('creator', models.ForeignKey(related_name='projects', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('worker_group', models.ForeignKey(related_name='project_as_worker', to='auth.Group')),
            ],
            options={
                'permissions': (('view_project', 'View Project'),),
            },
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(db_index=True, max_length=200, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('resource_file', models.FileField(max_length=255, upload_to=rodan.models.resource.upload_path, blank=True)),
                ('processing_status', models.IntegerField(blank=True, null=True, db_index=True, choices=[(0, b'Scheduled'), (1, b'Processing'), (4, b'Finished'), (-1, b'Failed'), (None, b'Not applicable')])),
                ('error_summary', models.TextField(default=b'')),
                ('error_details', models.TextField(default=b'')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('has_thumb', models.BooleanField(default=False, db_index=True)),
                ('creator', models.ForeignKey(related_name='resources', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('origin', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='rodan.Output', null=True)),
                ('project', models.ForeignKey(related_name='resources', to='rodan.Project')),
            ],
            options={
                'permissions': (('view_resource', 'View Resource'),),
            },
        ),
        migrations.CreateModel(
            name='ResourceType',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('mimetype', models.CharField(unique=True, max_length=50, db_index=True)),
                ('description', models.CharField(db_index=True, max_length=255, blank=True)),
                ('extension', models.CharField(db_index=True, max_length=50, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ResultsPackage',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('status', models.IntegerField(default=0, db_index=True, choices=[(0, b'Scheduled'), (1, b'Processing'), (4, b'Finished'), (-1, b'Failed'), (9, b'Cancelled'), (8, b'Expired')])),
                ('percent_completed', models.IntegerField(default=0, db_index=True)),
                ('packaging_mode', models.IntegerField(db_index=True, choices=[(0, b'Only endpoint resources'), (1, b'All resources -- subdirectoried by resource names'), (2, b'Diagnosis, including all inputs/outputs/settings -- subdirectoried by workflow job and resource names')])),
                ('celery_task_id', models.CharField(max_length=255, null=True, blank=True)),
                ('error_summary', models.TextField(default=b'', null=True, blank=True)),
                ('error_details', models.TextField(default=b'', null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('expiry_time', models.DateTimeField(db_index=True, null=True, blank=True)),
                ('creator', models.ForeignKey(related_name='results_packages', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'permissions': (('view_resultspackage', 'View ResultsPackage'),),
            },
        ),
        migrations.CreateModel(
            name='RunJob',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('workflow_job_uuid', models.CharField(max_length=32, db_index=True)),
                ('resource_uuid', models.CharField(db_index=True, max_length=32, null=True, blank=True)),
                ('job_name', models.CharField(max_length=200, db_index=True)),
                ('job_settings', jsonfield.fields.JSONField(default={})),
                ('status', models.IntegerField(default=0, db_index=True, choices=[(0, b'Scheduled'), (1, b'Processing'), (4, b'Finished'), (-1, b'Failed'), (9, b'Cancelled'), (2, b'Waiting for input')])),
                ('celery_task_id', models.CharField(max_length=255, null=True, blank=True)),
                ('error_summary', models.TextField(default=b'', null=True, blank=True)),
                ('error_details', models.TextField(default=b'', null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('interactive_timings', jsonfield.fields.JSONField(default=[])),
                ('working_user_token', models.UUIDField(null=True)),
                ('working_user_expiry', models.DateTimeField(null=True, db_index=True)),
                ('lock', models.CharField(max_length=50, null=True, blank=True)),
            ],
            options={
                'permissions': (('view_runjob', 'View RunJob'),),
            },
        ),
        migrations.CreateModel(
            name='Workflow',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(max_length=100, db_index=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('valid', models.BooleanField(default=False, db_index=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('creator', models.ForeignKey(related_name='workflows', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('project', models.ForeignKey(related_name='workflows', to='rodan.Project')),
            ],
            options={
                'permissions': (('view_workflow', 'View Workflow'),),
            },
        ),
        migrations.CreateModel(
            name='WorkflowJob',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('job_settings', jsonfield.fields.JSONField(default={}, null=True, blank=True)),
                ('name', models.CharField(db_index=True, max_length=255, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now=True, db_index=True)),
            ],
            options={
                'permissions': (('view_workflowjob', 'View WorkflowJob'),),
            },
        ),
        migrations.CreateModel(
            name='WorkflowJobCoordinateSet',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('data', jsonfield.fields.JSONField(default={}, null=True, blank=True)),
                ('user_agent', models.CharField(db_index=True, max_length=255, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('workflow_job', models.ForeignKey(related_name='workflow_job_coordinate_sets', to='rodan.WorkflowJob')),
            ],
            options={
                'permissions': (('view_workflowjobcoordinateset', 'View WorkflowJobCoordinateSet'),),
            },
        ),
        migrations.CreateModel(
            name='WorkflowJobGroup',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(max_length=100, db_index=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('origin', models.ForeignKey(related_name='used_as_workflow_job_groups', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='rodan.Workflow', null=True)),
                ('workflow', models.ForeignKey(related_name='workflow_job_groups', to='rodan.Workflow')),
            ],
            options={
                'permissions': (('view_workflowjobgroup', 'View WorkflowJobGroup'),),
            },
        ),
        migrations.CreateModel(
            name='WorkflowRun',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('status', models.IntegerField(default=1, db_index=True, choices=[(21, b'Request processing'), (1, b'Processing'), (4, b'Finished'), (-1, b'Failed'), (29, b'Request cancelling'), (9, b'Cancelled'), (31, b'Request retrying'), (11, b'Retrying')])),
                ('name', models.CharField(db_index=True, max_length=100, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now=True, db_index=True)),
                ('creator', models.ForeignKey(related_name='workflow_runs', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('last_redone_runjob_tree', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='rodan.RunJob', null=True)),
                ('project', models.ForeignKey(related_name='workflow_runs', to='rodan.Project')),
                ('workflow', models.ForeignKey(related_name='workflow_runs', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='rodan.Workflow', null=True)),
            ],
            options={
                'permissions': (('view_workflowrun', 'View WorkflowRun'),),
            },
        ),
        migrations.AddField(
            model_name='workflowjob',
            name='group',
            field=models.ForeignKey(related_name='workflow_jobs', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='rodan.WorkflowJobGroup', null=True),
        ),
        migrations.AddField(
            model_name='workflowjob',
            name='job',
            field=models.ForeignKey(related_name='workflow_jobs', on_delete=django.db.models.deletion.PROTECT, to='rodan.Job'),
        ),
        migrations.AddField(
            model_name='workflowjob',
            name='workflow',
            field=models.ForeignKey(related_name='workflow_jobs', to='rodan.Workflow'),
        ),
        migrations.AddField(
            model_name='runjob',
            name='workflow_job',
            field=models.ForeignKey(related_name='run_jobs', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='rodan.WorkflowJob', null=True),
        ),
        migrations.AddField(
            model_name='runjob',
            name='workflow_run',
            field=models.ForeignKey(related_name='run_jobs', to='rodan.WorkflowRun'),
        ),
        migrations.AddField(
            model_name='runjob',
            name='working_user',
            field=models.ForeignKey(related_name='interactive_runjobs', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='resultspackage',
            name='workflow_run',
            field=models.ForeignKey(related_name='results_packages', to='rodan.WorkflowRun'),
        ),
        migrations.AddField(
            model_name='resource',
            name='resource_type',
            field=models.ForeignKey(related_name='resources', on_delete=django.db.models.deletion.PROTECT, to='rodan.ResourceType'),
        ),
        migrations.AddField(
            model_name='outputporttype',
            name='resource_types',
            field=models.ManyToManyField(related_name='output_port_types', to='rodan.ResourceType'),
        ),
        migrations.AddField(
            model_name='outputport',
            name='output_port_type',
            field=models.ForeignKey(to='rodan.OutputPortType', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='outputport',
            name='workflow_job',
            field=models.ForeignKey(related_name='output_ports', to='rodan.WorkflowJob'),
        ),
        migrations.AddField(
            model_name='output',
            name='output_port',
            field=models.ForeignKey(related_name='outputs', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='rodan.OutputPort', null=True),
        ),
        migrations.AddField(
            model_name='output',
            name='resource',
            field=models.ForeignKey(related_name='outputs', on_delete=django.db.models.deletion.PROTECT, to='rodan.Resource'),
        ),
        migrations.AddField(
            model_name='output',
            name='run_job',
            field=models.ForeignKey(related_name='outputs', to='rodan.RunJob'),
        ),
        migrations.AddField(
            model_name='inputporttype',
            name='job',
            field=models.ForeignKey(related_name='input_port_types', to='rodan.Job'),
        ),
        migrations.AddField(
            model_name='inputporttype',
            name='resource_types',
            field=models.ManyToManyField(related_name='input_port_types', to='rodan.ResourceType'),
        ),
        migrations.AddField(
            model_name='inputport',
            name='input_port_type',
            field=models.ForeignKey(to='rodan.InputPortType', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='inputport',
            name='workflow_job',
            field=models.ForeignKey(related_name='input_ports', to='rodan.WorkflowJob'),
        ),
        migrations.AddField(
            model_name='input',
            name='input_port',
            field=models.ForeignKey(related_name='inputs', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='rodan.InputPort', null=True),
        ),
        migrations.AddField(
            model_name='input',
            name='resource',
            field=models.ForeignKey(related_name='inputs', on_delete=django.db.models.deletion.PROTECT, to='rodan.Resource'),
        ),
        migrations.AddField(
            model_name='input',
            name='run_job',
            field=models.ForeignKey(related_name='inputs', to='rodan.RunJob'),
        ),
        migrations.AddField(
            model_name='connection',
            name='input_port',
            field=models.ForeignKey(related_name='connections', to='rodan.InputPort'),
        ),
        migrations.AddField(
            model_name='connection',
            name='output_port',
            field=models.ForeignKey(related_name='connections', to='rodan.OutputPort'),
        ),
        migrations.AlterUniqueTogether(
            name='workflowjobcoordinateset',
            unique_together=set([('user_agent', 'workflow_job')]),
        ),
    ]
