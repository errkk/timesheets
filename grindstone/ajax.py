from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from models import Task, TaskAlias
import simplejson

@csrf_exempt
@login_required
@permission_required('grindstone.consolodate_task')
def ajax_consolodate_tasks(request):
	'''
	Get all aliases for the task (subject) and set their task_id to target
	Also remove the old task
	'''

	if 'PUT' == request.method:
		data = simplejson.loads(request.body)
		if 'subject' in data and 'target' in data:
			subject = Task.objects.get(pk=int(data['subject']))
			target = Task.objects.get(pk=int(data['target']))

			# All aliases for subject now should refer to target
			aliases_to_change = TaskAlias.objects.filter(task=subject)
			for a in aliases_to_change:
				a.task = target
				a.save()
			# Remove old task
			subject.delete()

	return HttpResponse( simplejson.dumps({'status':'ok','data':len(aliases_to_change)}) )