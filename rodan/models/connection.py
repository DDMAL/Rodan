import uuid
from django.db import models
from rodan.models.workflow import Workflow

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
    - `from_db` -- store workflow-invalidation-related fields.
    """
    class Meta:
        app_label = 'rodan'
        permissions = (
            ('view_connection', 'View Connection'),
        )

    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    input_port = models.ForeignKey('rodan.InputPort', related_name='connections', on_delete=models.CASCADE, db_index=True)
    output_port = models.ForeignKey('rodan.OutputPort', related_name='connections', on_delete=models.CASCADE, db_index=True)

    _rodan_custom_data = {}
    def _rodan_custom_store_fields(self):
        self._rodan_custom_data['original_input_port_id'] = self.input_port_id
        self._rodan_custom_data['original_output_port_id'] = self.output_port_id
        self._rodan_custom_data['original_workflow1_id'] = self.input_port.workflow_job.workflow_id
        self._rodan_custom_data['original_workflow2_id'] = self.output_port.workflow_job.workflow_id

    @classmethod
    def from_db(cls, *args, **kwargs):
        instance = super(Connection, cls).from_db(*args, **kwargs)
        instance._rodan_custom_store_fields()
        return instance

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
        cond1 = self.input_port_id != self._rodan_custom_data.get('original_input_port_id')
        cond2 = self.output_port_id != self._rodan_custom_data.get('original_output_port_id')
        wf1_original_id = self._rodan_custom_data.get('original_workflow1_id')
        wf1_new_id = self.input_port.workflow_job.workflow_id
        wf2_original_id = self._rodan_custom_data.get('original_workflow2_id')
        wf2_new_id = self.output_port.workflow_job.workflow_id
        super(Connection, self).save(*args, **kwargs)
        if cond1 or cond2:
            Workflow.objects.filter(pk__in=list(set([wf1_original_id, wf1_new_id, wf2_original_id, wf2_new_id]))).update(valid=False)

    def delete(self, *args, **kwargs):
        wf1_id = self.output_port.workflow_job.workflow_id
        wf2_id = self.input_port.workflow_job.workflow_id
        super(Connection, self).delete(*args, **kwargs)
        Workflow.objects.filter(pk__in=list(set([wf1_id, wf2_id]))).update(valid=False)

    def __unicode__(self):
        return u"<Connection {0}>".format(str(self.uuid))
