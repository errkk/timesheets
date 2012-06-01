from django.conf.urls import patterns, include, url
from views import dump, assign_alias, edit_task, list_tasks, delete_task, all_tasks

urlpatterns = patterns('',
	url(r'^dump', dump, name = 'dump' ),
	url(r'^alias/(?P<id>\d+)$', assign_alias, name = 'assign_alias' ),
	url(r'^task/(?P<id>\d+)$', edit_task, name = 'edit_task' ),
	url(r'^task/rm/(?P<id>\d+)$', delete_task, name = 'delete_task' ),
	url(r'^tasks/all', all_tasks, name = 'all_tasks' ),
	url(r'^tasks', list_tasks, name = 'list_tasks' ),
)