from django.db import models
from uuidfield import UUIDField
from rodan.models import OutputPortType


class Output(models.Model):
    """
    An `Output` is the result of performing a job on the specific input `Resource`s.
    There must be one `Output` for each `OutputPort` in the `RunJob`'s associated
    `WorkflowJob`.

    **Fields**

    - `uuid`
    - `output_port` -- a reference to an `OutputPort`. It should be set to None when the
      original `OutputPort` is deleted.
    - `output_port_type_name` -- a string containing the name of the `OutputPortType`.
    - `run_job` -- a reference to the `RunJob` associated with this `Output`.
    - `resource` -- the precise `Resource` that is output by the `RunJob` at
      the above-referenced `OutputPort`.

    **Properties**

    - `output_port_type` -- the corresponding `OutputPortType` object.
    """
    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    output_port = models.ForeignKey('rodan.OutputPort', related_name='outputs', blank=True, null=True, on_delete=models.SET_NULL)
    output_port_type_name = models.CharField(max_length=255)
    run_job = models.ForeignKey('rodan.RunJob', related_name='outputs')
    resource = models.ForeignKey('rodan.Resource', related_name='outputs')

    def __unicode__(self):
        return u"<Output {0}>".format(str(self.uuid))

    @property
    def output_port_type(self):
        try:
            return OutputPortType.objects.get(job=self.run_job, name=self.output_port_type_name)
        except OutputPortType.DoesNotExist:
            return None
