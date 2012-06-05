from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.core import serializers
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from forms import LoginForm, AliasForm, TaskForm
from django.contrib.auth import authenticate, login, logout
from models import ImportEvent, Interval, Task, TaskAlias
from django.contrib.auth.models import User
import datetime
from django.db.models import Count
from helpers import str2dt

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

		# Check there is anything new to import
		if len(tasks) > 0:
			imp = ImportEvent()
			imp.user = request.user
			imp.save()

			for t in tasks:
				ivl = Interval()
				# Find proper task name
				ivl.get_or_create_alias( t['name'], imp.user )
				ivl.duration = t['total']
				ivl.importevent = imp
				ivl.start = t['start']
				ivl.end = t['end']
				ivl.save()
				print ivl
		else:
			data = simplejson.dumps( {'status':'uptodate'} )
			return HttpResponse( data )

		data = map( lambda i: {'name':i['name'],'total':str(i['total'])}, tasks )
	
		data = simplejson.dumps( {'status':'ok', 'data' : data } )

		return HttpResponse( data )
	else:
		return HttpResponse( 'false' )

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
				return HttpResponseRedirect(reverse('assign_alias', args=[id]))

		# Save alias against chosen task
		elif form.is_valid():
			obj = form.save()
			request.notifications.success('Thanks, now %s is known as %s' % ( alias.string, obj.task ) )
			return HttpResponseRedirect(reverse('assign_alias', args=[id]))
		else:
			pass

	else:
		form = AliasForm(instance = alias)


	return render(request,'assign_alias.html', { 
		'title' : '"%s"' % alias.string, 
		'form' : form,
		'success_url' : reverse('home') 
	})

@login_required
@permission_required('change_task')
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
@permission_required('change_task')
def list_tasks(request):
	tasks = Task.objects.all()
	return render(request,'listing.html', { 'title' : 'Edit Tasks', 'objects' : tasks })

@login_required
@permission_required('delete_task')
def delete_task(request,id):
	task = get_object_or_404( Task, pk=id )
	
	if task.delete():
		request.notifications.success( 'Task Deleted' )
	
	return HttpResponseRedirect( reverse('list_tasks') )


@login_required
def all_tasks(request,datefrom=None,dateto=None):

	# Try to get date info
	if datefrom and dateto:		
		try:	
			datefrom, dateto = str2dt(datefrom), str2dt(dateto)			
		except ValueError:
			return HttpResponseRedirect( reverse('all_tasks') )
		else:
			# Filterr envents between date range, as no exception was caught converting DT
			aliases = TaskAlias.objects.filter( task__isnull = False ).filter( interval__start__gte = datefrom, interval__end__lte = dateto ).annotate(terms=Count('task'))
	else:
		aliases = TaskAlias.objects.filter( task__isnull = False ).annotate(terms=Count('task'))

		

	# Blank stuff for containing output form the itterations
	a = {}
	categories = []
	values = []
	tasks = []


	# Group TaskAlias instances in a list for each proper task, 
	# task ID is used for the key to identify uniqueness
	for i in aliases:
		if i.task.pk in a:
			a[i.task.pk].append(i)
		else:
			a[i.task.pk] = [i]

	# Loop thru list of proper tasks, some will be lists of more than one total that need to be totaled
	for i in a:
		if len(a[i]) > 1:
			# Make TD object for total time for all totals in this list
			total = sum([sub.task.get_total_time() for sub in a[i]], datetime.timedelta(0))			
			categories.append( a[i][0].task.name )
			values.append( total.seconds / 60 )
			tasks.append( {'name' : a[i][0].task.name, 'total' : total} )

		else:
			# Just one task alias for this proper task
			ta = a[i][0]
			total = ta.task.get_total_time()
			categories.append( ta.task.name )
			values.append( float( total.seconds / 60 ) )
			tasks.append( {'name' : ta.task.name, 'total' : total} )


	return render(request,'graph.html', { 
		'title' : 'All projects', 
		'tasks' : tasks,
		'categories' : simplejson.dumps( categories ),
		'values' : simplejson.dumps( values ),
		'date' : { 'from' : datefrom, 'to' : dateto },
		'base_url' : reverse( all_tasks )
		})

@login_required
def my_tasks(request,datefrom=None,dateto=None):

	# Try to get date info
	if datefrom and dateto:		
		try:	
			datefrom, dateto = str2dt(datefrom), str2dt(dateto)		
		except ValueError:
			dateto, datefrom = False, False
			# Show all events
			return HttpResponseRedirect( reverse('my_tasks') )
		else:
			# Filterr envents between date range
			aliases = TaskAlias.objects.filter( task__isnull = False ).filter( interval__importevent__user = request.user ).filter( interval__start__gte = datefrom, interval__end__lte = dateto ).distinct()			
	else:
		aliases = TaskAlias.objects.filter( task__isnull = False ).filter( interval__importevent__user = request.user ).distinct()


	# list of dictionaries containing task name and total time for template
	# This format is so its the same as all_tasks
	tasks = [ {'name':i.task.name, 'total':i.task.get_total_time()} for i in aliases ]

	# List of Task names
	categories = simplejson.dumps( [ i['name'] for i in tasks ] )
	# List of values
	values = simplejson.dumps( [ float(i['total'].seconds / 60 ) for i in tasks ] )

	return render(request,'graph.html', { 
		'title' : 'My projects', 
		'tasks' : tasks,
		'categories' : categories,
		'values' : values,
		'date' : { 'from' : datefrom, 'to' : dateto },
		'base_url' : reverse( my_tasks )
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
			all_tasks = Task.objects.filter( taskalias__interval__start__gte = datefrom, taskalias__interval__end__lte = dateto ).distinct()
	else:
		all_tasks = Task.objects.all().distinct()

	# All users
	users = User.objects.filter( importevent__isnull = False )
	
	# List of string task names (categories)
	task_names = [ t.name for t in all_tasks ]

	# list to append for each user a dict with their name and a list of all the total times for all tasks
	data = []

	# each user, all tasks
	for u in users:
		# List of time (totals) for this user for every task in all_tasks
		series = []

		for t in all_tasks:
			# collect intervals for this user for this task
			intervals = Interval.objects.filter( alias__task = t ).filter( importevent__user = u )
			
			# Date filter
			if datefrom and dateto:
				intervals = intervals.filter( importevent__user = u ).filter( start__gte = datefrom, end__lte = dateto )

			if intervals:
				# Sum intervals for this task, to create total time this user has spent on it
				timedeltas = [ i.duration for i in intervals ]
				total = sum( timedeltas, datetime.timedelta(0) )
				total_mins = float( total.seconds / 60 )
				series.append(total_mins)
			else:
				# No intervals recorded so send 0 to keep list lined up
				series.append(0)

		data.append( { 'name' : str(u), 'data' : series } )

		
	
	return render(request,'graph_people.html', { 
		'title' : 'Projects', 
		'tasks' : all_tasks,
		'series' : simplejson.dumps(data),
		'categories' : simplejson.dumps(task_names),
		'date' : { 'from' : datefrom, 'to' : dateto },
		'base_url' : reverse( people_tasks )
		})

