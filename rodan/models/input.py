from django.db import models
from uuidfield import UUIDField


class Input(models.Model):
    """
    Links a `RunJob` to one of its input `Resource`s. There must be
    one `Input` for each `InputPort` of the `WorkflowJob`.

    **Fields**

    - `uuid`
    - `input_port` -- a reference to an `InputPort`.
    - `resource` -- a field containing a reference to the precise `Resource` that
      this `RunJob` will act on.
    - `run_job` -- a reference to the `RunJob` that will be executed.
    """
    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    input_port = models.ForeignKey('rodan.InputPort', related_name='inputs')
    resource = models.ForeignKey('rodan.Resource', related_name='inputs')
    run_job = models.ForeignKey('rodan.RunJob', related_name='inputs')

    def __unicode__(self):
        return u"<Input {0}>".format(str(self.uuid))
