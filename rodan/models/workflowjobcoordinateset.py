from django.db import models
from uuidfield import UUIDField
from jsonfield import JSONField


class WorkflowJobCoordinateSet(models.Model):
    """
    A `WorkflowJobCoordinateSet` contains the x and y coordinates of the center
    position of a `WorkflowJob` for a general or particular user agent.

    **Fields**

    - `uuid`
    - `workflow_job` -- a reference to the `WorkflowJob`.
    - `data` -- a JSON field including: `x` -- coordinate of the center position (% of the canvas size); `y` -- `y` coordinate of the center position (% of the canvas size); `width` -- relative width regarding the canvas size; `height` -- relative height regarding the canvas size; `color` (optional) -- CSS color code.
    - `user_agent` -- (optional) the name of user agent.
    - `created`
    - `updated`
    """
    uuid = UUIDField(primary_key=True, auto=True)
    workflow_job = models.ForeignKey('rodan.WorkflowJob', related_name="workflow_job_coordinate_sets", on_delete=models.CASCADE)
    data = JSONField(default={}, blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"<WorkflowJobCoordinateSet {0}>".format(str(self.uuid))

    class Meta:
        app_label = 'rodan'
        unique_together = ('user_agent', 'workflow_job')
