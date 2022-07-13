# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import sortedm2m.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('rodan', '0002_add_workflowjobgroupcoordinateset'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResourceList',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(db_index=True, max_length=200, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated', models.DateTimeField(auto_now=True, db_index=True)),
            ],
            options={
                'permissions': (('view_resourcelist', 'View ResourceList'),),
            },
        ),
        migrations.AddField(
            model_name='inputporttype',
            name='is_list',
            field=models.BooleanField(default=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='outputporttype',
            name='is_list',
            field=models.BooleanField(default=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='input',
            name='resource',
            field=models.ForeignKey(related_name='inputs', on_delete=django.db.models.deletion.PROTECT, blank=True, to='rodan.Resource', null=True),
        ),
        migrations.AlterField(
            model_name='output',
            name='resource',
            field=models.ForeignKey(related_name='outputs', on_delete=django.db.models.deletion.PROTECT, blank=True, to='rodan.Resource', null=True),
        ),
        migrations.AddField(
            model_name='resourcelist',
            name='origin',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='rodan.Output', null=True),
        ),
        migrations.AddField(
            model_name='resourcelist',
            name='project',
            field=models.ForeignKey(blank=True, to='rodan.Project', null=True),
        ),
        migrations.AddField(
            model_name='resourcelist',
            name='resource_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='rodan.ResourceType', null=True),
        ),
        migrations.AddField(
            model_name='resourcelist',
            name='resources',
            field=sortedm2m.fields.SortedManyToManyField(help_text=None, to='rodan.Resource'),
        ),
        migrations.AddField(
            model_name='input',
            name='resource_list',
            field=models.ForeignKey(related_name='inputs', on_delete=django.db.models.deletion.PROTECT, blank=True, to='rodan.ResourceList', null=True),
        ),
        migrations.AddField(
            model_name='output',
            name='resource_list',
            field=models.ForeignKey(related_name='outputs', on_delete=django.db.models.deletion.PROTECT, blank=True, to='rodan.ResourceList', null=True),
        ),
    ]
