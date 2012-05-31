from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.core import serializers
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse

import simplejson
import base64
import process_xml


def home(request):

		return render( request,'index.html', {} )

@csrf_exempt
def dump(request):

	if 'POST' in request.method:
	
		b64 = str(request.body).replace('data:text/xml;base64,','')

		xml = base64.urlsafe_b64decode( b64 )
	
		tasks = process_xml.get_tasks( xml, weeks = 1 )

		data = map( lambda i: {'name':i['name'],'total':str(i['total'])}, tasks )
	
		data = simplejson.dumps( data )

		return HttpResponse( data )
	else:
		return HttpResponse( 'false' )
