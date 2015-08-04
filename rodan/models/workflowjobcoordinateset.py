from django.db import models
from uuidfield import UUIDField


class WorkflowJobCoordinateSet(models.Model):
    """
    A `WorkflowJobCoordinateSet` contains the x and y coordinates of the center
    position of a `WorkflowJob` for a general or particular user agent.

    **Fields**

    - `uuid`
    - `workflow_job` -- a reference to the `WorkflowJob`.
    - `x` -- `x` coordinate of the center position (% of the canvas size).
    - `y` -- `y` coordinate of the center position (% of the canvas size).
    - `user_agent` -- (optional) the name of user agent.
    - `created`
    - `updated`
    """
    uuid = UUIDField(primary_key=True, auto=True)
    workflow_job = models.ForeignKey('rodan.WorkflowJob', related_name="workflow_job_coordinate_sets", on_delete=models.CASCADE)
    x = models.PositiveSmallIntegerField()
    y = models.PositiveSmallIntegerField()
    user_agent = models.CharField(max_length=255, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"<WorkflowJobCoordinateSet {0}>".format(str(self.uuid))

    class Meta:
        app_label = 'rodan'
