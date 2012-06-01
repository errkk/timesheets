from django import forms
from models import TaskAlias, Task

class LoginForm(forms.Form):
	username = forms.CharField(label='Username')
	password = forms.CharField(widget=forms.PasswordInput,label='Password')

class AliasForm(forms.ModelForm):
	class Meta:
		model = TaskAlias
		fields = ['task']

class TaskForm(forms.ModelForm):
	class Meta:
		model = Task