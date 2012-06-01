from datetime import timedelta

def sum_tds(timedeltas):
	'''
	Sum a list of timedelta objects
	'''
	return sum( timedeltas, timedelta(0) )