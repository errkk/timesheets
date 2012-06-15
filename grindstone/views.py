from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.core import serializers
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from forms import LoginForm, AliasForm, TaskForm
from django.contrib.auth import authenticate, login, logout
from models import ImportEvent, Interval, Task, TaskAlias, get_or_create_alias
from django.contrib.auth.models import User
import datetime
from django.db.models import Count
from helpers import str2dt, sum_tds, month_list

import simplejson
import base64
import process_xml

@login_required
def home(request):
	# Find my stats
	imports = ImportEvent.objects.filter(user = request.user).order_by('date')
	
	# Get all the tasks that this person has done
	aliases = TaskAlias.objects.filter( interval__importevent__user = request.user ).distinct()
	return render( request,'index.html', { 'mytasks' : aliases, 'imports' : imports } )

@login_required
@csrf_exempt
def dump(request):

	if 'POST' in request.method:

		now = datetime.datetime.now()

		# Find last import
		try:
			last_import = ImportEvent.objects.filter(user=request.user).order_by('-date')[0]
		except IndexError:
			last_import = False

		# Find how long ago it was and set delta period
		if last_import:
			delta_period = now - last_import.date.replace( tzinfo=None )
		else:
			delta_period = datetime.timedelta( weeks=2 )

		# Import Uploaded XML Data
		b64 = str(request.body).replace('data:text/xml;base64,','')

		xml = base64.urlsafe_b64decode( b64 )

		# Get tasks out of the XML	
		tasks = process_xml.get_tasks( xml, delta_period )

		if len(tasks) > 0:
			# Create import event
			imp = ImportEvent()
			imp.user = request.user
			imp.save()

			for t in tasks:
				# Find or create a TaskAlias for this task
				alias = get_or_create_alias( t['name'], request.user )

				# If there are time intervals recored, make an instance of Interval for each
				if len(t['intervals']) > 0:
					# There is time recorded for this task

					# Create interval record for all time intervals
					for i in t['intervals']:

						ivl = Interval()
						ivl.alias = alias
						ivl.importevent = imp
						ivl.duration = i['timedelta']
						ivl.start = i['start']
						ivl.end = i['end']
						ivl.save()

				else:
					# No tasks delivered, probably already done for this time period
					json = simplejson.dumps( {'status':'uptodate'} )
					return HttpResponse( json )

			# Return names of tasks that were imported
			data = [ {'name':i['name']} for i in tasks ]
			json = simplejson.dumps( {'status':'ok', 'data' : data } )
			return HttpResponse( json )
	

@csrf_protect
def loginpage(request):

	# Submitted Form
	if request.method == 'POST':
		# Bound To POST
		form = LoginForm(request.POST)

		if form.is_valid():
			# No Errors process form
			username = request.POST['username']
			password = request.POST['password']
			next = request.GET['next'] if 'next' in request.GET else '/'

			user = authenticate(username=username, password=password)

			if user is not None:
				if user.is_active:
					login(request, user)
					# Redirect to a success page.
					return HttpResponseRedirect(next)

				else:
					# Return a 'disabled account' error message
					request.notifications.error('Disabled account')
			else:
				request.notifications.error('Your username password combination was incorrect')
				# Return an 'invalid login' error message.

	else:
		# Unbound Form
		form = LoginForm()


	return render(request,'formpage.html', {
		'form':form
		})

def logoutpage(request):
	logout(request)
	return HttpResponseRedirect('/')

@login_required
def assign_alias(request,id):
	alias = get_object_or_404( TaskAlias, pk = id )

	if 'POST' == request.method:
		form = AliasForm( request.POST, instance = alias )
		form.fields['task'].queryset = Task.objects.all().order_by('name')

		# Make a task from this alias
		if 'makeonefromthis' in form.data:
			# Check this already hasnt been done
			existing = Task.objects.filter(name=alias.string)
			if existing:
				request.notifications.error('Looks like you have already done this')
				return HttpResponseRedirect(reverse('assign_alias', args=[id]))

			else:
				# No existing task with this name, create one based on this alias
				task = Task()
				task.name = alias.string
				task.save()

				alias.task = task
				alias.save()
				request.notifications.success('Proper task created from alias')
				return HttpResponseRedirect(reverse('home'))

		# Save alias against chosen task
		elif form.is_valid():
			obj = form.save()
			request.notifications.success('Thanks, now %s is known as %s' % ( alias.string, obj.task ) )
			return HttpResponseRedirect(reverse('home'))
		else:
			pass

	else:
		form = AliasForm(instance = alias)
		form.fields['task'].queryset = Task.objects.all().order_by('name')


	return render(request,'assign_alias.html', { 
		'title' : '"%s"' % alias.string, 
		'form' : form,
		'success_url' : reverse('home') 
	})

@login_required
@permission_required('grindstone.change_task')
def edit_task(request,id):
	task = get_object_or_404( Task, pk=id )

	if 'POST' == request.method:
		form = TaskForm( request.POST, instance = task )

		if form.is_valid():

			form.save()
			request.notifications.success('Task Updated' )
			return HttpResponseRedirect( reverse('list_tasks') )

	else:
		form = TaskForm(instance = task)

	return render(request,'formpage.html', { 'title' : 'Edit Task', 'form' : form })


@login_required
@permission_required('grindstone.change_task')
def list_tasks(request):
	tasks = Task.objects.all()
	return render(request,'listing.html', { 'title' : 'Edit Tasks', 'objects' : tasks, 'ajax_url' : reverse( 'ajax_consolodate_tasks' ) })

@login_required
@permission_required('grindstone.delete_task')
def delete_task(request,id):
	task = get_object_or_404( Task, pk=id )
	
	if task.delete():
		request.notifications.success( 'Task Deleted' )
	
	return HttpResponseRedirect( reverse('list_tasks') )


@login_required
def all_tasks_redirect(request):
	return HttpResponseRedirect( reverse('all_tasks') )

@login_required
def all_tasks(request,datefrom=None,dateto=None):

	# Try to get date info
	if datefrom and dateto:		
		try:	
			datefrom, dateto = str2dt(datefrom), str2dt(dateto)			
		except ValueError:
			# Show all
			return HttpResponseRedirect( reverse('all_tasks') )

	# Get all proper task objects
	mtasks = Task.objects.all()

	# Empty list for each task to send to the template
	tasks = []

	for t in mtasks:
		# Get all intervals for this task
		intervals = Interval.objects.filter( alias__task = t )

		# Filter by date if datetimes are present
		if datefrom and dateto:
			intervals = intervals.filter( start__gte = datefrom, end__lte = dateto )

		# Sum timedeltas for all the intervals for this task in this time period
		total = sum_tds( [ i.duration for i in intervals ] )

		# Append this task, and total time to the list for the template
		tasks.append({ 'name':t.name, 'total':total })

	# JSON List of Task names
	categories = simplejson.dumps( [ i['name'] for i in tasks ] )
	# JSON List of values
	values = simplejson.dumps( [ float(i['total'].seconds / 60 ) for i in tasks ] )

	# Get list of last 12 months for the selectbox, see helpers.py
	months = month_list( datefrom=datefrom, dateto=dateto )


	return render(request,'graph.html', { 
		'title' : 'All projects', 
		'tasks' : tasks,
		'categories' : categories,
		'values' : values,
		'date' : { 'from' : datefrom, 'to' : dateto },
		'base_url' : reverse( all_tasks ),
		'months' : months,
		'datefrom' : datefrom.strftime('%Y-%m-%d') if datefrom else False,
		'dateto' : dateto.strftime('%Y-%m-%d') if dateto else False
		})





@login_required
def my_tasks(request,datefrom=None,dateto=None):

	# Get all tasks for this user
	aliases = TaskAlias.objects.filter( task__isnull = False ).filter( interval__importevent__user = request.user ).distinct()

	# Filter aliases if there is some datetimes
	if datefrom and dateto:		
		try:	
			datefrom, dateto = str2dt(datefrom), str2dt(dateto)		
		except ValueError:
			dateto, datefrom = False, False
			# Show all
			return HttpResponseRedirect( reverse('my_tasks') )
	
	# Empty list for each task to send to the template
	tasks = []

	# Loop thru aliases for this user, 
	# and find via all aliases for that (proper) task, find total time (for this user)
	for a in aliases:

		# Get all intervals for this task for this user
		intervals = Interval.objects.filter( alias__task = a.task ).filter( importevent__user = request.user )

		# Filter by date if datetimes are present
		if datefrom and dateto:
			intervals = intervals.filter( start__gte = datefrom, end__lte = dateto )

		# Sum timedeltas for all the intervals for this task in this time period
		total = sum_tds( [ i.duration for i in intervals ] )

		# Append this task, and total time to the list for the template
		tasks.append({ 'name':a.task.name, 'total':total })

	# JSON List of Task names
	categories = simplejson.dumps( [ i['name'] for i in tasks ] )
	# JSON List of values
	values = simplejson.dumps( [ float(i['total'].seconds / 60 ) for i in tasks ] )

	# Get list of last 12 months for the selectbox, see helpers.py
	months = month_list( datefrom=datefrom, dateto=dateto )

	return render(request,'graph.html', { 
		'title' : 'My projects', 
		'tasks' : tasks,
		'categories' : categories,
		'values' : values,
		'date' : { 'from' : datefrom, 'to' : dateto },
		'base_url' : reverse( my_tasks ),
		'months'	: months,
		'datefrom' : datefrom.strftime('%Y-%m-%d') if datefrom else False,
		'dateto' : dateto.strftime('%Y-%m-%d') if dateto else False
		})





@login_required
def people_tasks(request,datefrom=None,dateto=None):

	# Try to get date info
	if datefrom and dateto:		
		try:	
			datefrom, dateto = str2dt(datefrom), str2dt(dateto)		
		except ValueError:
			dateto, datefrom = False, False
			# Show all events
			return HttpResponseRedirect( reverse('my_tasks') )
		else:
			mtasks = Task.objects.filter( taskalias__interval__start__gte = datefrom, taskalias__interval__end__lte = dateto ).distinct()
	else:
		mtasks = Task.objects.all().distinct()

	# All users
	users = User.objects.filter( importevent__isnull = False ).distinct()
	
	# List of string task names (categories)
	task_names = [ t.name for t in mtasks ]

	# list to append for each user a dict with their name and a list of all the total times for all tasks
	data = []

	# each user, all tasks
	for u in users:
		# List of time (totals) for this user for every task in mtasks
		series = []

		for t in mtasks:
			# collect intervals for this user for this task
			intervals = Interval.objects.filter( alias__task = t ).filter( importevent__user = u )
			
			# Date filter
			if datefrom and dateto:
				intervals = intervals.filter( start__gte = datefrom, end__lte = dateto )

			if intervals:
				# Sum intervals for this task, to create total time this user has spent on it
				total = sum_tds( [ i.duration for i in intervals ] )
				total_mins = float( total.seconds / 60 )
				series.append(total_mins)
			else:
				# No intervals recorded so send 0 to keep list lined up
				series.append(0)

		data.append( { 'name' : str(u), 'data' : series } )

	# Get list of last 12 months for the selectbox, see helpers.py
	months = month_list( datefrom=datefrom, dateto=dateto )

		
	
	return render(request,'graph_people.html', { 
		'title' : 'Projects', 
		'tasks' : mtasks,
		'series' : simplejson.dumps(data),
		'categories' : simplejson.dumps(task_names),
		'date' : { 'from' : datefrom, 'to' : dateto },
		'base_url' : reverse( people_tasks ),
		'months' : months,
		'datefrom' : datefrom.strftime('%Y-%m-%d') if datefrom else False,
		'dateto' : dateto.strftime('%Y-%m-%d') if dateto else False
		})

