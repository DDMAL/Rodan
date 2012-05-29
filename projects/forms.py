from django.forms import ModelForm
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
        exclude = ('rodan_users',)
        model = Job

class WorkflowForm(ModelForm):
    class Meta:
        model = Workflow

class PageForm(ModelForm):
    
    class Meta:
        exclude = ('image_name',
                   'workflow',
                   'project',)
        model = Page
