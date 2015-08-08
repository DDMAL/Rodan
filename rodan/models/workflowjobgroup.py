from django.db import models
from uuidfield import UUIDField


class WorkflowJobGroup(models.Model):
    """
    A `WorkflowJobGroup` is a container representing the grouping of `WorkflowJob`s.

    **Fields**

    - `uuid`
    - `origin` -- a nullable reference to the `Workflow` indicating where it comes
      from.
    """
    uuid = UUIDField(primary_key=True, auto=True)
    origin = models.ForeignKey("rodan.Workflow", related_name="workflow_job_groups", blank=True, null=True, on_delete=models.SET_NULL)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"<WorkflowJobGroup {0}>".format(str(self.uuid))

    class Meta:
        app_label = 'rodan'
