import os
from django.db import models
from uuidfield import UUIDField

class WorkflowRunStatus:
    IN_PROGRESS = 0
    HAS_FINISHED = 1
    FAILED = -1
    CANCELLED = 9

class WorkflowRun(models.Model):
    """
    Represents the running of a workflow. Since Rodan is based on a RESTful design,
    `Workflow`s are *not* run by sending a command like "run workflow". Rather,
    they are run by creating a new `WorkflowRun` instance.

    **Fields**

    - `uuid`
    - `workflow` -- a reference to the `Workflow`.
    - `creator` -- a reference to the `User`.
    - `test_run` [TODO]
    - `status` -- indicating the status of the `WorkflowRun`.
    - `created`
    - `updated`

    **Properties**

    - `workflow_run_path` [TODO]
    - `retry_backup_directory` [TODO]
    """
    STATUS_CHOICES = [(WorkflowRunStatus.IN_PROGRESS, "In progress"),
                      (WorkflowRunStatus.HAS_FINISHED, "Has finished"),
                      (WorkflowRunStatus.FAILED, "Failed, ZOMG"),
                      (WorkflowRunStatus.CANCELLED, "Cancelled")]
    @property
    def workflow_run_path(self):
        return os.path.join(self.workflow.workflow_path, "runs", str(self.pk))

    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    workflow = models.ForeignKey('rodan.Workflow', related_name="workflow_runs")
    creator = models.ForeignKey('auth.User', related_name="workflow_runs")
    test_run = models.BooleanField(default=False)  # [TODO]
    status = models.IntegerField(choices=STATUS_CHOICES, default=WorkflowRunStatus.IN_PROGRESS)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"<WorkflowRun {0}>".format(str(self.uuid))

    @property
    def retry_backup_directory(self):
        project_path = self.workflow.project.project_path
        return os.path.join(str(project_path), 'workflowrun_retry_backup')
