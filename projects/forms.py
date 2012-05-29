from django.forms import ModelForm
from projects.models import Project
from projects.models import Job
from projects.models import Workflow

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
        exclude = ('jobs',)
