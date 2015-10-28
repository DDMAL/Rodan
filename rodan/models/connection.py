import uuid
from django.db import models

class Connection(models.Model):
    """
    Describes exactly how `WorkflowJob`s are connected together. `InputPort` and
    `OutputPort` should be in the same `Workflow`. (Validation implemented in serializer)

    **Fields**

    - `uuid`
    - `input_port` -- a reference to the specific `InputPort` that is on
      the "input" end of the connection.
    - `output_port` -- a reference to the specific `OutputPort` that is on
      the "output" end of the connection.

    **Properties**

    - `input_workflow_job` -- the `WorkflowJob` instance associated with
      `input_port`.
    - `output_workflow_job` -- the `WorkflowJob` instance associated with
      `output_port`.
    - `workflow` -- the `Workflow` instance which the `WorkflowJob`s are a part of.

    **Methods**

    - `save` and `delete` -- invalidate the associated `Workflow`.
    """
    class Meta:
        app_label = 'rodan'
        permissions = (
            ('view_connection', 'View Connection'),
        )

    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    input_port = models.ForeignKey('rodan.InputPort', related_name='connections', on_delete=models.CASCADE, db_index=True)
    output_port = models.ForeignKey('rodan.OutputPort', related_name='connections', on_delete=models.CASCADE, db_index=True)

    @property
    def input_workflow_job(self):
        return self.input_port.workflow_job

    @property
    def output_workflow_job(self):
        return self.output_port.workflow_job

    @property
    def workflow(self):
        return self.output_port.workflow_job.workflow


    def save(self, *args, **kwargs):
        super(Connection, self).save(*args, **kwargs)
        wf = self.workflow
        wf.valid = False
        wf.save()  # always touch workflow to update the `update` field.

    def delete(self, *args, **kwargs):
        wf = self.workflow
        super(Connection, self).delete(*args, **kwargs)
        wf.valid = False
        wf.save()  # always touch workflow to update the `update` field.

    def __unicode__(self):
        return u"<Connection {0}>".format(str(self.uuid))
