from django.db import models
import uuid
from rodan.models.workflow import Workflow

class InputPort(models.Model):
    """
    Represents what a `WorkflowJob` will take when it is executed.

    The number of `InputPort`s for a particular `InputPortType` must be within the
    associated `InputPortType.minimum` and `InputPortType.maximum` values.

    **Fields**

    - `uuid`
    - `workflow_job` -- a foreign key reference to the associated `WorkflowJob`.
    - `input_port_type` -- a foreign key reference to associated `InputPortType`.
    - `label` -- an optional name unique to the other `InputPort`s in the `WorkflowJob`
      (only for the user).
    - `extern` -- an automatically set flag to distinguish an entry `InputPort` in a
      validated `Workflow`. If the `Workflow` is not valid, this field should be
      ignored.

    **Methods**

    - `save` and `delete` -- invalidate the associated `Workflow`.
    - `save` -- set `label` to the name of its associated `InputPortType` as a
      default value.
    - `from_db` -- store workflow-invalidation-related fields.
    """

    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    workflow_job = models.ForeignKey('rodan.WorkflowJob', related_name='input_ports', on_delete=models.CASCADE, db_index=True)
    input_port_type = models.ForeignKey('rodan.InputPortType', on_delete=models.PROTECT, db_index=True)
    label = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    extern = models.BooleanField(default=False, db_index=True)

    _rodan_custom_data = {}
    def _rodan_custom_store_fields(self):
        self._rodan_custom_data['original_workflow_job_id'] = self.workflow_job_id
        self._rodan_custom_data['original_input_port_type_id'] = self.input_port_type_id
        self._rodan_custom_data['original_workflow_id'] = self.workflow_job.workflow_id

    @classmethod
    def from_db(cls, *args, **kwargs):
        instance = super(InputPort, cls).from_db(*args, **kwargs)
        instance._rodan_custom_store_fields()
        return instance

    def save(self, *args, **kwargs):
        if not self.label:
            self.label = self.input_port_type.name
        cond1 = self.workflow_job_id != self._rodan_custom_data.get('original_workflow_job_id')
        cond2 = self.input_port_type_id != self._rodan_custom_data.get('original_input_port_type_id')
        wf_original_id = self._rodan_custom_data.get('original_workflow_id')
        wf_new_id = self.workflow_job.workflow_id
        super(InputPort, self).save(*args, **kwargs)
        if cond1 or cond2:
            Workflow.objects.filter(pk__in=list(set([wf_original_id, wf_new_id]))).update(valid=False)

    def delete(self, *args, **kwargs):
        wf_id = self.workflow_job.workflow_id
        super(InputPort, self).delete(*args, **kwargs)
        Workflow.objects.filter(pk=wf_id).update(valid=False)

    def __unicode__(self):
        return u"<InputPort {0}>".format(str(self.uuid))

    class Meta:
        app_label = 'rodan'
        permissions = (
            ('view_inputport', 'View InputPort'),
        )
