from django.db import models
from uuidfield import UUIDField


class Output(models.Model):
    """
    An `Output` is the result of performing a job on the specific input `Resource`s.
    There must be one `Output` for each `OutputPort` in the `RunJob`'s associated
    `WorkflowJob`.

    **Fields**

    - `uuid`
    - `output_port` -- a reference to an `OutputPort`.
    - `run_job` -- a reference to the `RunJob` associated with this `Output`.
    - `resource` -- the precise `Resource` that is output by the `RunJob` at
      the above-referenced `OutputPort`.
    - `created`
    - `updated`
    """
    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    output_port = models.ForeignKey('rodan.OutputPort', related_name='outputs')
    run_job = models.ForeignKey('rodan.RunJob', related_name='outputs')
    resource = models.ForeignKey('rodan.Resource', related_name='outputs')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"<Output {0}>".format(str(self.uuid))
