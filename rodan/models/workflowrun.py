import os
from django.db import models
from uuidfield import UUIDField
# from django_extensions.db.fields import json


class WorkflowRun(models.Model):
    @property
    def workflow_run_path(self):
        return os.path.join(self.workflow.workflow_path, "runs", str(self.pk))

    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    workflow = models.ForeignKey('rodan.Workflow', related_name="workflow_runs")
    run = models.IntegerField(default=1)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"<WorkflowRun {0}>".format(str(self.uuid))

    def save(self, *args, **kwargs):
        super(WorkflowRun, self).save(*args, **kwargs)
        if not os.path.exists(self.workflow_run_path):
            os.makedirs(self.workflow_run_path)
