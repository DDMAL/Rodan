import uuid
from django.db import models
from jsonfield import JSONField


class WorkflowJobGroup(models.Model):
    """
    A `WorkflowJobGroup` is a container representing the grouping of `WorkflowJob`s.

    **Fields**

    - `uuid`
    - `name`
    - `description`
    - `workflow` -- the `Workflow` that it belongs to.
    - `origin` -- a nullable reference to the `Workflow` indicating where it comes
      from.
    - `appearance` -- a JSON field including:
        `x` -- coordinate of the center position (% of the canvas size);
        `y` -- `y` coordinate of the center position (% of the canvas size);
        `width` -- relative width regarding the canvas size;
        `height` -- relative height regarding the canvas size;
        `color` (optional) -- CSS color code.

    - `created`
    - `updated`
    """

    class Meta:
        app_label = "rodan"
        permissions = (("view_workflowjobgroup", "View WorkflowJobGroup"),)

    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True, null=True)
    workflow = models.ForeignKey(
        "rodan.Workflow",
        related_name="workflow_job_groups",
        on_delete=models.CASCADE,
        db_index=True,
    )
    origin = models.ForeignKey(
        "rodan.Workflow",
        related_name="used_as_workflow_job_groups",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        db_index=True,
    )

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    appearance = JSONField(
        default={"x": 0.5, "y": 0.5},
    )

    def __unicode__(self):
        return u"<WorkflowJobGroup {0}>".format(str(self.uuid))
