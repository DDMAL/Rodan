import uuid
from django.db import models
from jsonfield import JSONField
from rodan.models.job import Job
from rodan.constants import task_status
from django.contrib.auth.models import User


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
    - `resource_uuid` -- a copy of the uuid of `Resource` in the resource collection,
      indicate the processing flow for every individual `Resource` in a batch. Allowed
      to be null when it is singleton `RunJob`.
    - `job_name` -- the Rodan `Job` name of this `RunJob`.
    - `job_queue` -- group of celery workers that can execute this `RunJob`.
    - `job_settings` -- the settings associated with the `WorkflowJob` that is
      being executed in the `RunJob`.
    - `status` -- an integer indicating the status of `RunJob`.
    - `celery_task_id` -- the corresponding Celery Task. This field is set after the
      `RunJob` starts running.
    - `error_summary` -- summary of error when the `RunJob` fails.
    - `error_details` -- details of error when the `RunJob` fails.
    - `created`
    - `updated`
    - `interactive_timings` -- a JSON list that tracks the start and end of every manual
      phase of the job.

    - `working_user` -- a nullable field indicating the working user of an interactive
      job. If it is None, or the time is after the expiry time, there are no user working
      with this job.
    - `working_user_token` -- a nullable field containing the unique token for the
      combination of user and `RunJob`, in order to authenticate user in the interactive
      interface of an interactive phase (where token auth is not applicable).
    - `working_user_expiry` -- a datetime field indicating the expiry of `working_user`.

    - `lock` -- (internal use) stores the thread identifier of one of Celery workers, or
      None. For a worker thread to lock the RunJobs and avoid competition. (see
      `rodan.jobs.master_task`)

    **Properties**

    - `job` -- the corresponding Rodan `Job` instance.
    - `interactive_relurl` -- the relative URL of interactive interface of the RunJob that
      needs user input.
    - `project` -- the corresponding Rodan `Project` instance.
    """

    class Meta:
        app_label = "rodan"
        permissions = (("view_runjob", "View RunJob"),)

    STATUS_CHOICES = [
        (task_status.SCHEDULED, "Scheduled"),
        (task_status.PROCESSING, "Processing"),
        (task_status.FINISHED, "Finished"),
        (task_status.FAILED, "Failed"),
        (task_status.CANCELLED, "Cancelled"),
        (task_status.WAITING_FOR_INPUT, "Waiting for input"),
    ]

    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    workflow_run = models.ForeignKey(
        "rodan.WorkflowRun",
        related_name="run_jobs",
        on_delete=models.CASCADE,
        db_index=True,
    )
    workflow_job = models.ForeignKey(
        "rodan.WorkflowJob",
        related_name="run_jobs",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        db_index=True,
    )

    workflow_job_uuid = models.CharField(max_length=32, db_index=True)
    resource_uuid = models.CharField(
        max_length=32, blank=True, null=True, db_index=True
    )
    job_name = models.CharField(max_length=200, db_index=True)
    job_queue = models.CharField(max_length=15, default="celery")
    job_settings = JSONField(default={})
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, db_index=True)
    celery_task_id = models.CharField(max_length=255, blank=True, null=True)

    error_summary = models.TextField(default="", blank=True, null=True)
    error_details = models.TextField(default="", blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    interactive_timings = JSONField(
        default=[]
    )  # track when a person starts and submits the job

    working_user = models.ForeignKey(
        User,
        related_name="interactive_runjobs",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_index=True,
    )
    working_user_token = models.UUIDField(null=True)
    working_user_expiry = models.DateTimeField(null=True, db_index=True)

    lock = models.CharField(max_length=50, blank=True, null=True)

    def __unicode__(self):
        return u"<RunJob {0} {1}>".format(str(self.uuid), self.job_name)

    @property
    def job(self):
        try:
            return Job.objects.get(name=self.job_name)
        except Job.DoesNotExist:
            return None

    @property
    def project(self):
        return self.workflow_run.project
