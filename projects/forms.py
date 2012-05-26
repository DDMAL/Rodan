from django.forms import ModelForm
from projects.models import Project

class ProjectForm(ModelForm):
    class Meta:
        exclude = ('rodan_users',)
        model = Project
