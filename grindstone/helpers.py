

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


def month_list( datefrom=None, dateto=None, length = 11):
	'''
	Make a list of dates for the last 12 months for sending to a selectbox in the template
	Pass datefrom and dateto to identify if its the current month and set selected to true
	They must be the full last and first days of the month.
	'''

	from datetime import datetime, timedelta
	from dateutil.relativedelta import relativedelta

	now = datetime.today()
	start_of_this_month = datetime( now.year, now.month, 1 )

	def month_maker(m):
		# Calculate datetimes for the start and end of the month
		start = start_of_this_month + relativedelta( months = -m )
		end = start + relativedelta( months = 1, days = -1 )
		nominal_td = timedelta(1) # 1 day
		# Check the start and end date in the URI are the last and first days of this month
		# Do that by comparing datetime objects, and the resulting timedeta that is smallest is the closest, smaller than datetime.timedelta(1)
		selected = datefrom and dateto and abs(datefrom - start) < nominal_td and abs(dateto - end) < nominal_td
		
		return { 'from' : start, 'to' : end, 'text': start.strftime('%B %Y'), 'selected' : selected }

	months = map( month_maker, xrange( 0, length ) )

	return months