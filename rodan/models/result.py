from django.db import models


class Result(models.Model):
    workflow_job = models.ForeignKey('rodan.WorkflowJob')
    page = models.ForeignKey('rodan.Page')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'rodan'
