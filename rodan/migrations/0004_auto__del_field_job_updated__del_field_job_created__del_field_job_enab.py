# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Job.updated'
        db.delete_column('rodan_job', 'updated')

        # Deleting field 'Job.created'
        db.delete_column('rodan_job', 'created')

        # Deleting field 'Job.enabled'
        db.delete_column('rodan_job', 'enabled')

        # Deleting field 'Job.module'
        db.delete_column('rodan_job', 'module')

        # Deleting field 'Job.slug'
        db.delete_column('rodan_job', 'slug')

        # Adding field 'Job.author'
        db.add_column('rodan_job', 'author',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Job.input_types'
        db.add_column('rodan_job', 'input_types',
                      self.gf('django.db.models.fields.TextField')(default='{}'),
                      keep_default=False)

        # Adding field 'Job.output_types'
        db.add_column('rodan_job', 'output_types',
                      self.gf('django.db.models.fields.TextField')(default='{}'),
                      keep_default=False)

        # Adding field 'Job.arguments'
        db.add_column('rodan_job', 'arguments',
                      self.gf('django.db.models.fields.TextField')(default='{}', null=True, blank=True),
                      keep_default=False)

        # Adding field 'Job.is_enabled'
        db.add_column('rodan_job', 'is_enabled',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Job.updated'
        raise RuntimeError("Cannot reverse this migration. 'Job.updated' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Job.created'
        raise RuntimeError("Cannot reverse this migration. 'Job.created' and its values cannot be restored.")
        # Adding field 'Job.enabled'
        db.add_column('rodan_job', 'enabled',
                      self.gf('django.db.models.fields.CharField')(default=True, max_length=255),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Job.module'
        raise RuntimeError("Cannot reverse this migration. 'Job.module' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Job.slug'
        raise RuntimeError("Cannot reverse this migration. 'Job.slug' and its values cannot be restored.")
        # Deleting field 'Job.author'
        db.delete_column('rodan_job', 'author')

        # Deleting field 'Job.input_types'
        db.delete_column('rodan_job', 'input_types')

        # Deleting field 'Job.output_types'
        db.delete_column('rodan_job', 'output_types')

        # Deleting field 'Job.arguments'
        db.delete_column('rodan_job', 'arguments')

        # Deleting field 'Job.is_enabled'
        db.delete_column('rodan_job', 'is_enabled')


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
            'result': ('picklefield.fields.PickledObjectField', [], {'default': 'None', 'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'PENDING'", 'max_length': '50'}),
            'task_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'traceback': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'rodan.job': {
            'Meta': {'object_name': 'Job'},
            'arguments': ('django.db.models.fields.TextField', [], {'default': "'{}'", 'null': 'True', 'blank': 'True'}),
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page_image': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'page_order': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pages'", 'to': "orm['rodan.Project']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'rodan.project': {
            'Meta': {'object_name': 'Project'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'projects'", 'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
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
            'description': ('django.db.models.fields.TextField', [], {}),
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