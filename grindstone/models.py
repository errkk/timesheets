from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from interval.fields import IntervalField
from helpers import sum_tds


class Category(models.Model):
	'''
	Group Tasks into categories for sorting and filtering
	'''
	name = models.CharField(null=True, blank=True, max_length=254)
	description = models.CharField(null=True, blank=True, max_length=500)

	def __unicode__(self):
		return self.name

class Task(models.Model):
	'''
	Official name for a task, as per Agnes
	'''
	name = models.CharField(null=False, blank=False, max_length=254)
	description = models.CharField(null=True, blank=True, max_length=500)
	categories = models.ManyToManyField(Category, null=True, blank=True)

	def __unicode__(self):
		return self.name

	def get_aliases(self,user=None):
		'Get all aliases for this task'
		aliases = TaskAlias.objects.filter( task = self )
		if user:
			aliases.filter( user = user )
		return aliases

	def get_total_time(self, user=None):
		'''
		Sum the total timedelta attached to all aliases of this task
		'''
		timedeltas = [ a.get_total_time() for a in self.get_aliases(user=user) ]
		return sum_tds( timedeltas )

	class Meta:
		permissions = (
			('consolodate_task', 'Can drag and drop tasks to consolodate them'),
		)




class TaskAlias(models.Model):
	'''
	Alternative wordings for a task as described by users in Grindstone
	'''
	task = models.ForeignKey(Task, null=True)
	string = models.CharField(null=False, blank=False, max_length=254)
	user = models.ForeignKey(User)

	def __unicode__(self):
		if self.task:
			name  = self.task.name
		else:
			name = 'Not Assigned!'
		return '%s (%s)' % ( self.string, name )

	def get_intervals(self):
		return Interval.objects.filter( alias = self )

	def get_total_time(self):
		intervals = self.get_intervals()
		timedeltas = [ i.duration for i in intervals ]
		total = sum_tds( timedeltas )

		return total


class ImportEvent(models.Model):
	'''
	Records when and who made a certain import of XML data from Grindstone
	'''
	user = models.ForeignKey(User)
	date = models.DateTimeField( auto_now_add = True, editable = True )

	def __unicode__(self):
		return '%s (%s)' % ( self.date, self.user )


class Interval(models.Model):
	'''
	Represents each period of time spent on a project per import
	'''
	alias = models.ForeignKey(TaskAlias)
	importevent = models.ForeignKey(ImportEvent)
	duration = IntervalField()
	start = models.DateTimeField(null=False,blank=False)
	end = models.DateTimeField(null=False,blank=False)

	def __unicode__(self):
		if self.alias.task:
			name = self.alias.task.name
		else:
			name = self.alias.string

		return '%s spend doing %s (%s)' % ( self.duration, name, self.importevent.user )



			
def get_or_create_alias(name, user):
		alias = TaskAlias.objects.filter(string=name, user = user)

		if alias and len(alias):
			return alias[0]
		else:
			# New alias assigned to new task
			alias = TaskAlias()
			alias.string = name
			alias.user = user
			alias.save()
			return alias



