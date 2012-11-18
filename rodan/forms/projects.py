from django import forms
from rodan.models.project import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        exclude = ('creator',)
        model = Project


class UploadFileForm(forms.Form):
    file = forms.FileField()
