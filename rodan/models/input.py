from django.db import models
from uuidfield import UUIDField
from rodan.models.inputporttype import InputPortType

class Input(models.Model):
    """
    Links a `RunJob` to one of its input `Resource`s. There must be
    one `Input` for each `InputPort` of the `WorkflowJob`.

    **Fields**

    - `uuid`
    - `input_port` -- a reference to an `InputPort`. It should be set to None when the
      original `InputPort` is deleted.
    - `input_port_type_name` -- a string containing the name of the `InputPortType`.
    - `resource` -- a field containing a reference to the precise `Resource` that
      this `RunJob` will act on.
    - `run_job` -- a reference to the `RunJob` that will be executed.

    **Properties**

    - `input_port_type` -- the corresponding `InputPortType` object.
    """
    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    input_port = models.ForeignKey('rodan.InputPort', related_name='inputs', blank=True, null=True, on_delete=models.SET_NULL)
    input_port_type_name = models.CharField(max_length=255)
    resource = models.ForeignKey('rodan.Resource', related_name='inputs', on_delete=models.PROTECT)
    run_job = models.ForeignKey('rodan.RunJob', related_name='inputs', on_delete=models.CASCADE)

    def __unicode__(self):
        return u"<Input {0}>".format(str(self.uuid))

    @property
    def input_port_type(self):
        try:
            return InputPortType.objects.get(job__name=self.run_job.job_name, name=self.input_port_type_name)
        except InputPortType.DoesNotExist:
            return None
