# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table('grindstone_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True)),
        ))
        db.send_create_signal('grindstone', ['Category'])

        # Adding model 'Task'
        db.create_table('grindstone_task', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True)),
        ))
        db.send_create_signal('grindstone', ['Task'])

        # Adding M2M table for field categories on 'Task'
        db.create_table('grindstone_task_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('task', models.ForeignKey(orm['grindstone.task'], null=False)),
            ('category', models.ForeignKey(orm['grindstone.category'], null=False))
        ))
        db.create_unique('grindstone_task_categories', ['task_id', 'category_id'])

        # Adding model 'TaskAlias'
        db.create_table('grindstone_taskalias', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['grindstone.Task'], null=True)),
            ('string', self.gf('django.db.models.fields.CharField')(max_length=254)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('grindstone', ['TaskAlias'])

        # Adding model 'ImportEvent'
        db.create_table('grindstone_importevent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('grindstone', ['ImportEvent'])

        # Adding model 'Interval'
        db.create_table('grindstone_interval', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('alias', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['grindstone.TaskAlias'])),
            ('importevent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['grindstone.ImportEvent'])),
            ('duration', self.gf('interval.fields.IntervalField')()),
            ('start', self.gf('django.db.models.fields.DateTimeField')()),
            ('end', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('grindstone', ['Interval'])


    def backwards(self, orm):
        # Deleting model 'Category'
        db.delete_table('grindstone_category')

        # Deleting model 'Task'
        db.delete_table('grindstone_task')

        # Removing M2M table for field categories on 'Task'
        db.delete_table('grindstone_task_categories')

        # Deleting model 'TaskAlias'
        db.delete_table('grindstone_taskalias')

        # Deleting model 'ImportEvent'
        db.delete_table('grindstone_importevent')

        # Deleting model 'Interval'
        db.delete_table('grindstone_interval')


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
        'grindstone.category': {
            'Meta': {'object_name': 'Category'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '254'})
        },
        'grindstone.importevent': {
            'Meta': {'object_name': 'ImportEvent'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'grindstone.interval': {
            'Meta': {'object_name': 'Interval'},
            'alias': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['grindstone.TaskAlias']"}),
            'duration': ('interval.fields.IntervalField', [], {}),
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'importevent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['grindstone.ImportEvent']"}),
            'start': ('django.db.models.fields.DateTimeField', [], {})
        },
        'grindstone.task': {
            'Meta': {'object_name': 'Task'},
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['grindstone.Category']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '254'})
        },
        'grindstone.taskalias': {
            'Meta': {'object_name': 'TaskAlias'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'string': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['grindstone.Task']", 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['grindstone']