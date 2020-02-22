from django.db import models
from jsonfield import JSONField
import uuid


class WorkflowJobGroupCoordinateSet(models.Model):
    """
    A `WorkflowJobGroupCoordinateSet` contains the x and y coordinates of the center
    position of a `WorkflowJobGroup` for a general or particular user agent.

    **Fields**

    - `uuid`
    - `workflow_job_group` -- a reference to the `WorkflowJobGroup`.
    - `data` -- a JSON field including:
        `x` -- coordinate of the center position (% of the canvas size);
        `y` -- `y` coordinate of the center position (% of the canvas size);
        `width` -- relative width regarding the canvas size;
        `height` -- relative height regarding the canvas size;
        `color` (optional) -- CSS color code.
    - `user_agent` -- (optional) the name of user agent.
    - `created`
    - `updated`
    """

    class Meta:
        app_label = "rodan"
        unique_together = ("user_agent", "workflow_job_group")
        permissions = (
            (
                "view_workflowjobgroupcoordinateset",
                "View WorkflowJobGroupCoordinateSet",
            ),
        )

    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    workflow_job_group = models.ForeignKey(
        "rodan.WorkflowJobGroup",
        related_name="workflow_job_group_coordinate_sets",
        on_delete=models.CASCADE,
        db_index=True,
    )
    data = JSONField(default={}, blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True, db_index=True)

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    def __unicode__(self):
        return u"<WorkflowJobGroupCoordinateSet {0}>".format(str(self.uuid))
