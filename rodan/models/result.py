import os
from django.db import models
import uuid
from rodan.models.workflowjob import WorkflowJob
from rodan.models.page import Page
from uuidfield import UUIDField


class Result(models.Model):

    @property
    def result_path(self):
        return os.path.join("projects", str(self.page.project.pk), "pages", str(self.page.pk), "results", str(self.uuid))

    def upload_fn(self, filename):
        _, ext = os.path.splitext(os.path.basename(filename))
        return os.path.join(self.result_path, "{0}{1}".format(str(uuid.uuid4()), ext))

    uuid = UUIDField(primary_key=True, auto=True)
    task_name = models.CharField(max_length=255)
    workflow_job = models.ForeignKey(WorkflowJob, null=True)
    page = models.ForeignKey(Page)
    result = models.FileField(upload_to=upload_fn, null=True, blank=True, max_length=255)

    # for interactive jobs: If this is set to True the job will not run.
    # set it to false to allow it to run.
    needs_input = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'rodan'
