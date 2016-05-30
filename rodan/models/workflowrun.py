import os
import uuid
from django.db import models
from rodan.constants import task_status
import shutil

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
    - `status` -- indicating the status of the `WorkflowRun`.

    - `name` -- user's name to the `WorkflowRun`.
    - `description` -- user's description of the `WorkflowRun`.

    - `last_redone_runjob_tree` -- a nullable reference to `RunJob`, indicating the root
      of `RunJob` tree last redone.

    - `created`
    - `updated`

    **Properties**

    - `origin_resources` -- a list of origin `Resource` UUIDs.
    """
    STATUS_CHOICES = [(task_status.REQUEST_PROCESSING, "Request processing"),
                      (task_status.PROCESSING, "Processing"),
                      (task_status.FINISHED, "Finished"),
                      (task_status.FAILED, "Failed"),
                      (task_status.REQUEST_CANCELLING, "Request cancelling"),
                      (task_status.CANCELLED, "Cancelled"),
                      (task_status.REQUEST_RETRYING, "Request retrying"),
                      (task_status.RETRYING, "Retrying")]

    class Meta:
        app_label = 'rodan'
        permissions = (
            ('view_workflowrun', 'View WorkflowRun'),
        )

    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    project = models.ForeignKey('rodan.Project', related_name="workflow_runs", on_delete=models.CASCADE, db_index=True)
    workflow = models.ForeignKey('rodan.Workflow', related_name="workflow_runs", blank=True, null=True, on_delete=models.SET_NULL, db_index=True)
    creator = models.ForeignKey('auth.User', related_name="workflow_runs", blank=True, null=True, on_delete=models.SET_NULL, db_index=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=task_status.PROCESSING, db_index=True)

    name = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    description = models.TextField(blank=True, null=True)

    last_redone_runjob_tree = models.ForeignKey('rodan.RunJob', related_name="+", blank=True, null=True, on_delete=models.SET_NULL)

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    @property
    def origin_resources(self):
        return list(set(self.run_jobs.values_list('resource_uuid', flat=True)))

    def __unicode__(self):
        return u"<WorkflowRun {0}>".format(str(self.uuid))

    def delete(self, *args, **kwargs):
        # remove protected links from runjobs to workflowrun by deleting the jobruns
        from rodan.models import RunJob
        RunJob.objects.filter(workflow_run=self).delete()
        # if os.path.exists(self.resource_path):
        #     shutil.rmtree(self.resource_path)
        super(WorkflowRun, self).delete(*args, **kwargs)