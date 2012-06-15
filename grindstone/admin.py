from models import ImportEvent, Interval, Task, TaskAlias, Category
from django.contrib import admin

class ImportEventAdmin(admin.ModelAdmin):
	list_display = ('date', 'user')
	list_filter = ('date', 'user')

class IntervalAdmin(admin.ModelAdmin):
	list_display = ('task','duration','user')
	list_filter = ('alias',)

	def task(self, obj):
		return obj.alias.task

	def user(self, obj):
		return obj.alias.user

class TaskAliasAdmin(admin.ModelAdmin):
	list_display = ('string','task','user')
	list_filter = ('user','task')

class CategoryAdmin(admin.ModelAdmin):
	list_filter = ('task',)

admin.site.register(ImportEvent, ImportEventAdmin)
admin.site.register(Interval,IntervalAdmin)
admin.site.register(Task)
admin.site.register(TaskAlias,TaskAliasAdmin)
admin.site.register(Category,CategoryAdmin)