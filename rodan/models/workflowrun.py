import os
from django.db import models
from uuidfield import UUIDField
from rodan.constants import task_status

class WorkflowRun(models.Model):
    """
    Represents the running of a workflow. Since Rodan is based on a RESTful design,
    `Workflow`s are *not* run by sending a command like "run workflow". Rather,
    they are run by creating a new `WorkflowRun` instance.

    **Fields**

    - `uuid`
    - `project` -- a reference to the `Project`.
    - `workflow` -- a reference to the `Workflow`. If the `Workflow` is deleted, this
      field will be set to None.
    - `workflow_name` -- a copy of the name of `Workflow`.
    - `creator` -- a reference to the `User`.
    - `test_run` -- indicating if the `WorkflowRun` is a test run.
    - `status` -- indicating the status of the `WorkflowRun`.
    - `created`
    - `updated`
    """
    STATUS_CHOICES = [(task_status.PROCESSING, "Processing"),
                      (task_status.FINISHED, "Finished"),
                      (task_status.FAILED, "Failed"),
                      (task_status.CANCELLED, "Cancelled"),
                      (task_status.RETRYING, "Retrying")]

    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    project = models.ForeignKey('rodan.Project', related_name="workflow_runs", blank=True, null=True, on_delete=models.SET_NULL)
    workflow = models.ForeignKey('rodan.Workflow', related_name="workflow_runs", blank=True, null=True, on_delete=models.SET_NULL)
    workflow_name = models.CharField(max_length=100)
    creator = models.ForeignKey('auth.User', related_name="workflow_runs")
    test_run = models.BooleanField(default=False)
    status = models.IntegerField(choices=STATUS_CHOICES, default=task_status.PROCESSING)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"<WorkflowRun {0}>".format(str(self.uuid))
