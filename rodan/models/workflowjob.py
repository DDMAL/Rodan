from django.db import models
import uuid
from jsonfield import JSONField
from rodan.jobs.deep_eq import deep_eq
from rodan.models.workflow import Workflow


class WorkflowJob(models.Model):
    """
    A `WorkflowJob` is an "instance" of a `Job`. `WorkflowJob`s connect to other
    `WorkflowJob`s, and this constitutes the control flow of the associated `Workflow`.
    How a `WorkflowJob` connects to another depends on their respective `InputPort`s
    and `OutputPort`s.

    **Fields**

    - `uuid`
    - `workflow` -- a reference to the `Workflow` that it belongs to.
    - `job` -- a reference to the `Job`.
    - `job_settings` -- JSON field. Store user's settings which correspond to the
      preset requirements of `Job` settings.
    - `name` -- user-defined name. Default: the same as `job_name`.

    - `group` -- a nullable reference to the `WorkflowGroup` object.

    **Properties**

    - `job_name` -- name of the referenced `Job`.
    - `job_description` -- description of the referenced `Job`.

    **Methods**

    - `save` and `delete` -- invalidate the referenced `Workflow` if `workflow`, `job`, or `job_settings` are touched.
    """

    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    workflow = models.ForeignKey(
        "rodan.Workflow",
        related_name="workflow_jobs",
        on_delete=models.CASCADE,
        db_index=True,
    )
    job = models.ForeignKey(
        "rodan.Job",
        related_name="workflow_jobs",
        on_delete=models.PROTECT,
        db_index=True,
    )
    job_settings = JSONField(default={}, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True, db_index=True)

    group = models.ForeignKey(
        "rodan.WorkflowJobGroup",
        related_name="workflow_jobs",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        db_index=True,
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.job_name.split(".")[-1]

        # [TODO] not too efficient... consider do the invalidation in db?
        try:
            old = WorkflowJob.objects.get(pk=self.pk)
        except WorkflowJob.DoesNotExist:
            old = WorkflowJob()  # empty
        cond1 = self.workflow_id != old.workflow_id
        cond2 = self.job_id != old.job_id
        cond3 = not deep_eq(self.job_settings, old.job_settings)
        super(WorkflowJob, self).save(*args, **kwargs)
        if cond1 or cond2 or cond3:
            wf_id = self.workflow_id
            Workflow.objects.filter(pk__in=list(set([wf_id, old.workflow_id]))).update(
                valid=False
            )

    def delete(self, *args, **kwargs):
        wf_id = self.workflow_id
        super(WorkflowJob, self).delete(*args, **kwargs)
        Workflow.objects.filter(pk=wf_id).update(valid=False)

    def __unicode__(self):
        return u"<WorkflowJob {0}>".format(str(self.uuid))

    class Meta:
        app_label = "rodan"
        permissions = (("view_workflowjob", "View WorkflowJob"),)

    @property
    def job_name(self):
        return self.job.name

    @property
    def job_description(self):
        return self.job.description
