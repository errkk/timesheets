import os
from BeautifulSoup import BeautifulSoup
from datetime import timedelta, datetime
import iso8601
import sys

def parse_date(string):
	return iso8601.parse_date( string ).replace( tzinfo=None )

def get_tasks( xml, delta_period ):
	soup = BeautifulSoup( xml )

	tasks = []
	
	now_limit = datetime.now()
	start_limit = now_limit - delta_period


	# Loop thru all tasks
	for task in soup.findAll('task'):
		
		name = task['name']

		# Find times for this task node
		times = task.findAll('time')
		times = filter( lambda t: start_limit <= parse_date( t['end'] ) <= now_limit, times )
						
		# Make timedelta objects for all the times in this task
		timedeltas = map( lambda t: timedelta( hours = int(t['hours']), minutes = int(t['minutes']), seconds = int(t['seconds']) ), times )

		# find the earliest and lated times for the components that make up this total
		starts = [ parse_date( t['start'] ) for t in times ]
		ends = [ parse_date( t['end'] ) for t in times ]

		starts.sort()
		ends.sort()

		# Append dict with the name and total time delta
		if len(times) > 0:
			tasks.append( { 'name' : name, 'total' : sum( timedeltas, timedelta() ), 'start' : starts[0], 'end' : ends[-1] } )

	# Sort by amount of time
	tasks.sort( key = lambda i: i['total'], reverse = True )

	# Filter tasks with no time
	tasks = filter( lambda i: i['total'] > timedelta(0,0,0), tasks )

	return tasks
