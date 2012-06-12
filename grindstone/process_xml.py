import os
from BeautifulSoup import BeautifulSoup
from datetime import timedelta, datetime
import iso8601
import sys


def parse_date(string):
	return iso8601.parse_date( string ).replace( tzinfo=None )

def get_td(t):
	return timedelta( hours = int(t['hours']), minutes = int(t['minutes']), seconds = int(t['seconds']) )

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

		# Get timing intervals starting within the limit of this import
		times = filter( lambda t: start_limit <= parse_date( t['end'] ) <= now_limit, times )
		
		# Make a dict with the start, finsih and total time for each timing interval
		intervals = [ { 'start' : parse_date( t['start'] ), 'end' : parse_date( t['end'] ), 'timedelta' : get_td(t) } for t in times ]

		# Add this task to the list to be returned if there are intervals timed for it
		if len(intervals) > 0:
			tasks.append({ 'name': name, 'intervals' : intervals })

	if len(tasks) > 0:
		return tasks
