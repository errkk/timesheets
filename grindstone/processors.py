from django.contrib.auth.models import User
from models import ImportEvent
from datetime import datetime, timedelta
from django.contrib import messages



def nag(request):
	today = datetime.today()
	td_week = timedelta(minutes=1)
	
	recent_imports = ImportEvent.objects.filter( date__lte=today, date__gte=today-td_week, user=request.user )
	
	if not bool(recent_imports):
		messages.add_message(request, messages.WARNING, 'Naughty! you havent uploaded your XML this week')

	return { 'recent_imports': recent_imports }

