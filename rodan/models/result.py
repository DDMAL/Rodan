import os
from django.db import models
from rodan.models.workflowjob import WorkflowJob
from rodan.models.page import Page
from uuidfield import UUIDField


class Result(models.Model):

    @property
    def upload_path(self):
        """ We will need to know the path where the results are being stored"""
        return os.path.join("projects", str(self.page.project.pk), "pages", str(self.page.pk), "results", str(self.uuid))

    def upload_fn(self, filename):
        path = self.upload_path
        return os.path.join(path, filename)

    uuid = UUIDField(primary_key=True, auto=True)
    workflow_job = models.ForeignKey(WorkflowJob)
    page = models.ForeignKey(Page)
    result = models.FileField(upload_to=upload_fn, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'rodan'
