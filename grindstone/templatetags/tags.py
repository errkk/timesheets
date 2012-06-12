from django import template
from django.core.urlresolvers import reverse

register = template.Library()

@register.tag
def activeparent(parser, token):
	args = token.split_contents()
	template_tag = args[0]
	if len(args) < 2:
		raise template.TemplateSyntaxError, "%r tag requires at least one argument" % template_tag
	return NavSelectedParentNode(args[1:])

class NavSelectedParentNode(template.Node):
	def __init__(self, name):
		self.name = name

	def render(self, context):
		
		if reverse(self.name[1]) in context['request'].path:
			return 'active'
		else:
			return ''

@register.tag
def active(parser, token):
	args = token.split_contents()
	template_tag = args[0]
	if len(args) < 2:
		raise template.TemplateSyntaxError, "%r tag requires at least one argument" % template_tag
	return NavSelectedNode(args[1:])

class NavSelectedNode(template.Node):
	def __init__(self, name):
		self.name = name

	def render(self, context):
		print reverse(self.name[1]), context['request'].path
		
		if reverse(self.name[1]) == context['request'].path:
			return 'active'
		else:
			return ''