# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Project'
        db.create_table('rodan_project', (
            ('uuid', self.gf('uuidfield.fields.UUIDField')(unique=True, max_length=32, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='projects', to=orm['auth.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('rodan', ['Project'])

        # Adding model 'Job'
        db.create_table('rodan_job', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('input_types', self.gf('django.db.models.fields.TextField')(default='{}')),
            ('output_types', self.gf('django.db.models.fields.TextField')(default='{}')),
            ('arguments', self.gf('django.db.models.fields.TextField')(default='{}', null=True, blank=True)),
            ('is_enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_automatic', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_required', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('rodan', ['Job'])

        # Adding model 'Page'
        db.create_table('rodan_page', (
            ('uuid', self.gf('uuidfield.fields.UUIDField')(unique=True, max_length=32, primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='pages', to=orm['rodan.Project'])),
            ('page_image', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True)),
            ('page_order', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('image_file_size', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='pages', null=True, to=orm['auth.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('rodan', ['Page'])

        # Adding model 'Workflow'
        db.create_table('rodan_workflow', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='workflows', to=orm['rodan.Project'])),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('has_started', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('rodan', ['Workflow'])

        # Adding M2M table for field pages on 'Workflow'
        db.create_table('rodan_workflow_pages', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('workflow', models.ForeignKey(orm['rodan.workflow'], null=False)),
            ('page', models.ForeignKey(orm['rodan.page'], null=False))
        ))
        db.create_unique('rodan_workflow_pages', ['workflow_id', 'page_id'])

        # Adding model 'WorkflowJob'
        db.create_table('rodan_workflowjob', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('workflow', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rodan.Workflow'])),
            ('job', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rodan.Job'])),
            ('sequence', self.gf('django.db.models.fields.IntegerField')()),
            ('job_settings', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('rodan', ['WorkflowJob'])

        # Adding model 'Result'
        db.create_table('rodan_result', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('workflow_job', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rodan.WorkflowJob'])),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rodan.Page'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('rodan', ['Result'])

        # Adding model 'ResultFile'
        db.create_table('rodan_resultfile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('result', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rodan.Result'])),
            ('result_type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('rodan', ['ResultFile'])

        # Adding model 'ResultTask'
        db.create_table('rodan_resulttask', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('result', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rodan.Result'])),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djcelery.TaskMeta'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('rodan', ['ResultTask'])


    def backwards(self, orm):
        # Deleting model 'Project'
        db.delete_table('rodan_project')

        # Deleting model 'Job'
        db.delete_table('rodan_job')

        # Deleting model 'Page'
        db.delete_table('rodan_page')

        # Deleting model 'Workflow'
        db.delete_table('rodan_workflow')

        # Removing M2M table for field pages on 'Workflow'
        db.delete_table('rodan_workflow_pages')

        # Deleting model 'WorkflowJob'
        db.delete_table('rodan_workflowjob')

        # Deleting model 'Result'
        db.delete_table('rodan_result')

        # Deleting model 'ResultFile'
        db.delete_table('rodan_resultfile')

        # Deleting model 'ResultTask'
        db.delete_table('rodan_resulttask')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'djcelery.taskmeta': {
            'Meta': {'object_name': 'TaskMeta', 'db_table': "'celery_taskmeta'"},
            'date_done': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meta': ('djcelery.picklefield.PickledObjectField', [], {'default': 'None', 'null': 'True'}),
            'result': ('djcelery.picklefield.PickledObjectField', [], {'default': 'None', 'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'PENDING'", 'max_length': '50'}),
            'task_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'traceback': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'rodan.job': {
            'Meta': {'object_name': 'Job'},
            'arguments': ('django.db.models.fields.TextField', [], {'default': "'{}'", 'null': 'True', 'blank': 'True'}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'input_types': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'is_automatic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'output_types': ('django.db.models.fields.TextField', [], {'default': "'{}'"})
        },
        'rodan.page': {
            'Meta': {'object_name': 'Page'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pages'", 'null': 'True', 'to': "orm['auth.User']"}),
            'image_file_size': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'page_image': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'page_order': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pages'", 'to': "orm['rodan.Project']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'uuid': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'primary_key': 'True'})
        },
        'rodan.project': {
            'Meta': {'object_name': 'Project'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'projects'", 'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'uuid': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'primary_key': 'True'})
        },
        'rodan.result': {
            'Meta': {'object_name': 'Result'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rodan.Page']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'workflow_job': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rodan.WorkflowJob']"})
        },
        'rodan.resultfile': {
            'Meta': {'object_name': 'ResultFile'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'result': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rodan.Result']"}),
            'result_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'rodan.resulttask': {
            'Meta': {'object_name': 'ResultTask'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'result': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rodan.Result']"}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djcelery.TaskMeta']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'rodan.workflow': {
            'Meta': {'object_name': 'Workflow'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'has_started': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jobs': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['rodan.Job']", 'null': 'True', 'through': "orm['rodan.WorkflowJob']", 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pages': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'workflows'", 'symmetrical': 'False', 'to': "orm['rodan.Page']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'workflows'", 'to': "orm['rodan.Project']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'rodan.workflowjob': {
            'Meta': {'object_name': 'WorkflowJob'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rodan.Job']"}),
            'job_settings': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sequence': ('django.db.models.fields.IntegerField', [], {}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rodan.Workflow']"})
        }
    }

    complete_apps = ['rodan']