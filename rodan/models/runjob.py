import os
import shutil
from django.db import models
from django.core.urlresolvers import reverse
from jsonfield import JSONField
from uuidfield import UUIDField
from rodan.models.resource import Resource
from rodan.models.job import Job
from rodan.models.input import Input
from rodan.models.output import Output
from rodan.constants import task_status

class RunJob(models.Model):
    """
    A `RunJob` is where a `WorkflowJob` gets executed as part of a `WorkflowRun`.
    The settings specified in the `WorkflowJob` are also kept track of in the `RunJob`.
    The `RunJob` specifies the exact individual `Resource`s the job is going to be
    applied to.

    **Fields**

    - `uuid`
    - `workflow_run` -- a reference to `WorkflowRun`.
    - `workflow_job` -- a reference to `WorkflowJob`. If the `WorkflowJob` is deleted,
      this field will be set to None.
    - `workflow_job_uuid` -- a copy of the uuid of `WorkflowJob`, to provide an identifier
      of its origin after the `WorkflowJob` is deleted.
    - `resource_uuid` -- a copy of the uuid of `Resource` in the `ResourceCollection`,
      indicate the processing flow for every individual `Resource` in a batch. Allowed
      to be null when it is singleton `RunJob`.
    - `job_name` -- the Rodan `Job` name of this `RunJob`.
    - `job_settings` -- the settings associated with the `WorkflowJob` that is
      being executed in the `RunJob`.
    - `status` -- an integer indicating the status of `RunJob`.
    - `celery_task_id` -- the corresponding Celery Task. This field is set after the
      `RunJob` starts running.
    - `error_summary` -- summary of error when the `RunJob` fails.
    - `error_details` -- details of error when the `RunJob` fails.
    - `created`
    - `updated`

    **Properties**

    - `job` -- the corresponding Rodan `Job` instance.
    - `interactive_relurl` -- the relative URL of interactive interface of the RunJob that
      needs user input.
    """
    STATUS_CHOICES = [(task_status.SCHEDULED, "Scheduled"),
                      (task_status.PROCESSING, "Processing"),
                      (task_status.FINISHED, "Finished"),
                      (task_status.FAILED, "Failed"),
                      (task_status.CANCELLED, "Cancelled"),
                      (task_status.WAITING_FOR_INPUT, "Waiting for input")]

    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    workflow_run = models.ForeignKey("rodan.WorkflowRun", related_name="run_jobs")
    workflow_job = models.ForeignKey("rodan.WorkflowJob", related_name="run_jobs", blank=True, null=True, on_delete=models.SET_NULL)

    workflow_job_uuid = models.CharField(max_length=32)
    resource_uuid = models.CharField(max_length=32, blank=True, null=True)
    job_name = models.CharField(max_length=200)

    job_settings = JSONField(default={})
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    celery_task_id = models.CharField(max_length=255, blank=True, null=True)

    error_summary = models.TextField(default="", blank=True, null=True)
    error_details = models.TextField(default="", blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"<RunJob {0} {1}{2}>".format(str(self.uuid), self.workflow_job.job.job_name, ' (interactive)' if self.workflow_job.job.interactive else '')

    @property
    def job(self):
        try:
            return Job.objects.get(job_name=self.job_name)
        except Job.DoesNotExist:
            return None

    @property
    def interactive_relurl(self):
        if self.status == task_status.WAITING_FOR_INPUT:
            return reverse('interactive', args=(self.uuid, ))
        else:
            return None
