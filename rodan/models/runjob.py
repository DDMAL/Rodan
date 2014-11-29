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
    WAITING_FOR_INPUT = 2 # [TODO] deprecated
    RUN_ONCE_WAITING = 3 # [TODO] deprecated
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

    - `job` -- the corresponding Rodan `Job` instance.
    - `workflow` -- the corresponding `Workflow` instance.
    """
    STATUS_CHOICES = [(RunJobStatus.NOT_RUNNING, "Not Running"),
                      (RunJobStatus.RUNNING, "Running"),
                      (RunJobStatus.HAS_FINISHED, "Has finished"),
                      (RunJobStatus.FAILED, "Failed, ZOMG"),
                      (RunJobStatus.CANCELLED, "Cancelled")]

    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    workflow_run = models.ForeignKey("rodan.WorkflowRun", related_name="run_jobs")
    workflow_job = models.ForeignKey("rodan.WorkflowJob", related_name="run_jobs")

    job_settings = json.JSONField(blank=True, null=True, default="[]")
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

    @property
    def job(self):
        return self.workflow_job.job

    @property
    def workflow(self):
        return self.workflow_run.workflow
