from django.db import models
from uuidfield import UUIDField


class OutputPortType(models.Model):
    """
    Defines what types of `Resource`s a `Job` will produce. Each `Job` must have
    1 or more `InputPortType`s.

    **Fields**

    - `uuid`
    - `job` -- the `Job` that this `OutputPortType` is associated with.
    - `name` -- a name unique to the other `OutputPortType`s in the `Job`.
    - `resource_types` -- a list of acceptable `ResourceType`s.
    - `minimum` -- the minimum number of `OutputPort`s of this `OutputPortType` a
      `WorkflowJob` must use in order to meet the execution requirements. It implies
      that this particular type of inputs may not be needed, or may need to be included
      more than once.
    - `maximum` -- the maximum number of `OutputPort`s of this `OutputPortType` a
      `WorkflowJob` may use in order to meet the execution requirements.
    """
    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    job = models.ForeignKey('rodan.Job', related_name='output_port_types')
    name = models.CharField(max_length=255)
    resource_types = models.ManyToManyField('rodan.ResourceType', related_name='output_port_types')
    minimum = models.IntegerField()
    maximum = models.IntegerField()

    def __unicode__(self):
        return u"<OutputPortType {0}>".format(str(self.uuid))
