import os
import shutil
from django.db import models
from django_extensions.db.fields import json
from uuidfield import UUIDField
from rodan.models.resource import Resource
from rodan.models.input import Input
from rodan.models.output import Output


class RunJobStatus(object):
    NOT_RUNNING = 0
    RUNNING = 1
    WAITING_FOR_INPUT = 2
    RUN_ONCE_WAITING = 3
    HAS_FINISHED = 4
    FAILED = -1
    CANCELLED = 9


class RunJob(models.Model):
    """
    A `RunJob` is where a `WorkflowJob` gets executed as part of a `WorkflowRun`.
    The settings specified in the `WorkflowJob` are also kept track of in the `RunJob`.
    The `RunJob` specifies the exact individual `Resource`s the job is going to be
    applied to.

    **Fields**

    - `uuid`
    - `workflow_run` -- a reference to `WorkflowRun`.
    - `workflow_job` -- a reference to `WorkflowJob`.
    - `job_settings` -- the settings associated with the `WorkflowJob` that is
      being executed in the `RunJob`.
    - `needs_input` -- a boolean. If true, indicate that the `RunJob` needs or will need
      user input.
    - `ready_for_input` -- a boolean. If true, indicate that the `RunJob` is currently
      ready for user input.
    - `status` -- an integer indicating the status of `RunJob`.
    - `celery_task_id` -- the corresponding Celery Task. This field is set after the
      `RunJob` starts running.
    - `error_summary` -- summary of error when the `RunJob` fails.
    - `error_details` -- details of error when the `RunJob` fails.
    - `created`
    - `updated`

    **Properties**

    - `runjob_path` [TODO] deprecated: we use resource paths now.
    - `job_name` -- the name of corresponding Rodan `Job`.
    - `workflow_name` -- the name of corresponding `Workflow`.

    **Methods**

    - `save` and `delete` [TODO] deprecated: we use resource paths now.
    """
    STATUS_CHOICES = [(RunJobStatus.NOT_RUNNING, "Not Running"),
                      (RunJobStatus.RUNNING, "Running"),
                      (RunJobStatus.WAITING_FOR_INPUT, "Waiting for input"), # [TODO] deprecated
                      (RunJobStatus.RUN_ONCE_WAITING, "Run once, waiting for input"), # [TODO] deprecated
                      (RunJobStatus.HAS_FINISHED, "Has finished"),
                      (RunJobStatus.FAILED, "Failed, ZOMG"),
                      (RunJobStatus.CANCELLED, "Cancelled")]

    @property
    def runjob_path(self):
        return os.path.join(self.workflow_run.workflow_run_path, "{0}_{1}".format(self.workflow_job.job_name, str(self.pk)))

    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    workflow_run = models.ForeignKey("rodan.WorkflowRun", related_name="run_jobs")
    workflow_job = models.ForeignKey("rodan.WorkflowJob", related_name="run_jobs")

    job_settings = json.JSONField(blank=True, null=True)
    needs_input = models.BooleanField(default=False)
    ready_for_input = models.BooleanField(default=False)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    celery_task_id = models.CharField(max_length=255, blank=True, null=True)

    error_summary = models.TextField(default="", blank=True, null=True)
    error_details = models.TextField(default="", blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"<RunJob {0} {1} ({2})>".format(str(self.uuid), self.workflow_job.job.job_name, self.needs_input)

    def save(self, *args, **kwargs):
        super(RunJob, self).save(*args, **kwargs)
        if not os.path.exists(self.runjob_path):
            os.makedirs(self.runjob_path)
        self.workflow_run.save()

    def delete(self, *args, **kwargs):
        if os.path.exists(self.runjob_path):
            shutil.rmtree(self.runjob_path)
        super(RunJob, self).delete(*args, **kwargs)

    @property
    def job_name(self):
        return self.workflow_job.job_name

    @property
    def workflow_name(self):
        return self.workflow_run.workflow.name
