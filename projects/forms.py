from django.forms import ModelForm
from django import forms
from projects.models import Project
from projects.models import Job
from projects.models import Workflow
from projects.models import Page

class ProjectForm(ModelForm):
    class Meta:
        exclude = ('rodan_users',)
        model = Project

class JobForm(ModelForm):
    class Meta:
        model = Job

class WorkflowForm(ModelForm):
    class Meta:
        model = Workflow
        exclude =  ('jobs',)

class PageForm(ModelForm):
    
    class Meta:
        exclude = ('image_name',
                   'workflow',
                   'project',)
        model = Page

class PageUploadForm(forms.Form):
    path_to_image = forms.FileField()
