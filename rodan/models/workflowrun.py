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
    - `creator` -- a reference to the `User`.
    - `test_run` [TODO]
    - `status` -- indicating the status of the `WorkflowRun`.
    - `created`
    - `updated`

    **Properties**

    - `workflow_run_path` [TODO]
    - `retry_backup_directory` [TODO]
    """
    STATUS_CHOICES = [(task_status.PROCESSING, "Processing"),
                      (task_status.FINISHED, "Finished"),
                      (task_status.FAILED, "Failed, ZOMG"),
                      (task_status.CANCELLED, "Cancelled")]
    @property
    def workflow_run_path(self):
        return os.path.join(self.workflow.workflow_path, "runs", str(self.pk))

    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    project = models.ForeignKey('rodan.Project', related_name="workflow_runs", blank=True, null=True, on_delete=models.SET_NULL)
    workflow = models.ForeignKey('rodan.Workflow', related_name="workflow_runs", blank=True, null=True, on_delete=models.SET_NULL)
    creator = models.ForeignKey('auth.User', related_name="workflow_runs")
    test_run = models.BooleanField(default=False)  # [TODO]
    status = models.IntegerField(choices=STATUS_CHOICES, default=task_status.PROCESSING)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"<WorkflowRun {0}>".format(str(self.uuid))

    @property
    def retry_backup_directory(self):
        project_path = self.workflow.project.project_path
        return os.path.join(str(project_path), 'workflowrun_retry_backup')
