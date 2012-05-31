from django.db import models



class Task(models.Model):
	name = models.CharField(null=False, blank=False, max_length=254)
	description = models.CharField(null=True, blank=True, max_length=500)
	
	def __unicode__(self):
		return self.name

class TaskName(models.Model):
	'''
	Alternative wordings for a task as described by users in Grindstone
	'''
	Task = models.ForeignKey(Task)
	string = models.CharField(null=False, blank=False, max_lenght=254)

	def __unicode__(self):
		return '%s (%s)' % ( self.string, self.Task.name )