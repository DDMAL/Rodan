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
            ('uuid', self.gf('uuidfield.fields.UUIDField')(unique=True, max_length=32, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('input_types', self.gf('django.db.models.fields.TextField')(default='{}', null=True, blank=True)),
            ('output_types', self.gf('django.db.models.fields.TextField')(default='{}', null=True, blank=True)),
            ('arguments', self.gf('django.db.models.fields.TextField')(default='{}', null=True, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('interactive', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('rodan', ['Job'])

        # Adding model 'Workflow'
        db.create_table('rodan_workflow', (
            ('uuid', self.gf('uuidfield.fields.UUIDField')(unique=True, max_length=32, primary_key=True)),
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
            ('uuid', self.gf('uuidfield.fields.UUIDField')(unique=True, max_length=32, primary_key=True)),
            ('workflow', self.gf('django.db.models.fields.related.ForeignKey')(related_name='wjobs', to=orm['rodan.Workflow'])),
            ('job', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rodan.Job'])),
            ('sequence', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('job_settings', self.gf('django.db.models.fields.TextField')(default='{}', null=True, blank=True)),
            ('job_type', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('rodan', ['WorkflowJob'])

        # Adding model 'Page'
        db.create_table('rodan_page', (
            ('uuid', self.gf('uuidfield.fields.UUIDField')(unique=True, max_length=32, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default=False, max_length=255, null=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='pages', to=orm['rodan.Project'])),
            ('page_image', self.gf('django.db.models.fields.files.FileField')(max_length=255, null=True)),
            ('compat_page_image', self.gf('django.db.models.fields.files.FileField')(max_length=255, null=True)),
            ('page_order', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('image_file_size', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('processed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='pages', null=True, to=orm['auth.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('rodan', ['Page'])

        # Adding model 'Result'
        db.create_table('rodan_result', (
            ('uuid', self.gf('uuidfield.fields.UUIDField')(unique=True, max_length=32, primary_key=True)),
            ('task_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('workflow_job', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rodan.WorkflowJob'], null=True)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rodan.Page'])),
            ('result', self.gf('django.db.models.fields.files.FileField')(max_length=255, null=True, blank=True)),
            ('needs_input', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('rodan', ['Result'])


    def backwards(self, orm):
        # Deleting model 'Project'
        db.delete_table('rodan_project')

        # Deleting model 'Job'
        db.delete_table('rodan_job')

        # Deleting model 'Workflow'
        db.delete_table('rodan_workflow')

        # Removing M2M table for field pages on 'Workflow'
        db.delete_table('rodan_workflow_pages')

        # Deleting model 'WorkflowJob'
        db.delete_table('rodan_workflowjob')

        # Deleting model 'Page'
        db.delete_table('rodan_page')

        # Deleting model 'Result'
        db.delete_table('rodan_result')


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
        'rodan.job': {
            'Meta': {'ordering': "['category']", 'object_name': 'Job'},
            'arguments': ('django.db.models.fields.TextField', [], {'default': "'{}'", 'null': 'True', 'blank': 'True'}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'input_types': ('django.db.models.fields.TextField', [], {'default': "'{}'", 'null': 'True', 'blank': 'True'}),
            'interactive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'output_types': ('django.db.models.fields.TextField', [], {'default': "'{}'", 'null': 'True', 'blank': 'True'}),
            'uuid': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'primary_key': 'True'})
        },
        'rodan.page': {
            'Meta': {'object_name': 'Page'},
            'compat_page_image': ('django.db.models.fields.files.FileField', [], {'max_length': '255', 'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pages'", 'null': 'True', 'to': "orm['auth.User']"}),
            'image_file_size': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': 'False', 'max_length': '255', 'null': 'True'}),
            'page_image': ('django.db.models.fields.files.FileField', [], {'max_length': '255', 'null': 'True'}),
            'page_order': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'needs_input': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rodan.Page']"}),
            'result': ('django.db.models.fields.files.FileField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'task_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'uuid': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'workflow_job': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rodan.WorkflowJob']", 'null': 'True'})
        },
        'rodan.workflow': {
            'Meta': {'object_name': 'Workflow'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'has_started': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'jobs': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'workflows'", 'blank': 'True', 'through': "orm['rodan.WorkflowJob']", 'to': "orm['rodan.Job']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pages': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'workflows'", 'blank': 'True', 'to': "orm['rodan.Page']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'workflows'", 'to': "orm['rodan.Project']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'uuid': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'primary_key': 'True'})
        },
        'rodan.workflowjob': {
            'Meta': {'ordering': "['sequence']", 'object_name': 'WorkflowJob'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rodan.Job']"}),
            'job_settings': ('django.db.models.fields.TextField', [], {'default': "'{}'", 'null': 'True', 'blank': 'True'}),
            'job_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sequence': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'uuid': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'primary_key': 'True'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'wjobs'", 'to': "orm['rodan.Workflow']"})
        }
    }

    complete_apps = ['rodan']