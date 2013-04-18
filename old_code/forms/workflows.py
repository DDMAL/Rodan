from django import forms
from rodan.models.workflow import Workflow


class WorkflowForm(forms.ModelForm):
    class Meta:
        exclude = ('jobs', 'has_started', 'project')
        model = Workflow
