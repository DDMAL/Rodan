from django.db import models
from uuidfield import UUIDField

class InputPortType(models.Model):
    """
    Defines what types of `Resource`s a `Job` expects to work with. Each `Job` may have
    0 or more `InputPortType`s.

    **Fields**

    - `uuid`
    - `job` -- the `Job` that this `InputPortType` is associated with.
    - `name` -- a name unique to the other `InputPortType`s in the `Job`.
    - `resource_types` -- a list of acceptable `ResourceType`s.
    - `minimum` -- the minimum number of `InputPort`s of this `InputPortType` a
      `WorkflowJob` must use in order to meet the execution requirements. It implies
      that this particular type of inputs may not be needed, or may need to be included
      more than once.
    - `maximum` -- the maximum number of `InputPort`s of this `InputPortType` a
      `WorkflowJob` may use in order to meet the execution requirements.
    """
    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    job = models.ForeignKey('rodan.Job', related_name='input_port_types', on_delete=models.CASCADE, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    resource_types = models.ManyToManyField('rodan.ResourceType', related_name='input_port_types')
    minimum = models.IntegerField(db_index=True)
    maximum = models.IntegerField(db_index=True)

    def __unicode__(self):
        return u"<InputPortType {0}>".format(str(self.uuid))
