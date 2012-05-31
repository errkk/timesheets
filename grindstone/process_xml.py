import os
from BeautifulSoup import BeautifulSoup
from datetime import timedelta, datetime
import iso8601
import sys

def get_tasks( xml, weeks = 1 ):
	soup = BeautifulSoup( xml )

	tasks = []
	
	now_limit = datetime.now()
	start_limit = now_limit - timedelta(weeks=weeks)


	# Loop thru all tasks
	for task in soup.findAll('task'):
		
		name = task['name']

		# Find times for this task node
		times = task.findAll('time')
		times = filter( lambda t: start_limit <= iso8601.parse_date( t['end'] ).replace( tzinfo=None ) <= now_limit, times )
						
		# Make timedelta objects for all the times in this task
		timedeltas = map( lambda t: timedelta( hours = int(t['hours']), minutes = int(t['minutes']), seconds = int(t['seconds']) ), times )

		# Append tuple with the name and total time delta
		tasks.append( { 'name' : name, 'total' : sum( timedeltas, timedelta() ) } )

	# Sort by amount of time
	tasks.sort( key = lambda i: i['total'], reverse = True )

	# Filter tasks with no time
	tasks = filter( lambda i: i['total'] > timedelta(0,0,0), tasks )

	return tasks
