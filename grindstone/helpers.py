

def sum_tds(timedeltas):
	'''
	Sum a list of timedelta objects
	'''
	from datetime import timedelta
	return sum( timedeltas, timedelta(0) )

def str2dt(string,format=None):
	'Make a datetime object from a standard date string YYYY-MM-DD'
	from datetime import datetime
	from time import mktime, strptime

	if not format:
		format = '%Y-%m-%d'

	return datetime.fromtimestamp(mktime(strptime( string, format )))