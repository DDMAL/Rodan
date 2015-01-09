from django.db import models
from rodan.models.job import Job
from rodan.models.workflow import Workflow
from jsonfield import JSONField
from uuidfield import UUIDField


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

    **Properties**

    - `job_name` -- name of the referenced `Job`.
    - `job_description` -- description of the referenced `Job`.

    **Methods**

    - `save` and `delete` -- invalidate the referenced `Workflow`.
    """
    uuid = UUIDField(primary_key=True, auto=True)
    workflow = models.ForeignKey(Workflow, related_name="workflow_jobs")
    job = models.ForeignKey(Job, related_name="workflow_jobs")
    job_settings = JSONField(default={}, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super(WorkflowJob, self).save(*args, **kwargs)
        wf = self.workflow
        wf.valid = False
        wf.save()  # always touch workflow to update the `update` field.

    def delete(self, *args, **kwargs):
        wf = self.workflow
        super(WorkflowJob, self).delete(*args, **kwargs)
        wf.valid = False
        wf.save()  # always touch workflow to update the `update` field.


    def __unicode__(self):
        return u"<WorkflowJob {0}>".format(str(self.uuid))

    class Meta:
        app_label = 'rodan'

    @property
    def job_name(self):
        return self.job.job_name

    @property
    def job_description(self):
        return self.job.description
