from django.conf.urls import patterns, include, url
from views import dump

urlpatterns = patterns('',
	url(r'^dump', dump, name = 'dump' ),
)