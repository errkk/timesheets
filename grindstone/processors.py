from django.contrib.auth.models import User
from models import ImportEvent
from datetime import datetime, timedelta
from django.contrib import messages



def nag(request):

	today = datetime.today()
	td_week = timedelta(weeks=1)
	try:
		recent_imports = ImportEvent.objects.filter( date__lte=today, date__gte=today-td_week, user=request.user )
	except:
		recent_imports = False

	if not bool(recent_imports) and request.user.is_authenticated():
		messages.add_message(request, messages.WARNING, 'Naughty! you havent uploaded your XML this week')

	return { 'recent_imports': recent_imports }

