from django.db import models
import uuid
from rodan.models.workflow import Workflow

class OutputPort(models.Model):
    """
    Represents what a `WorkflowJob` will produce when it is executed.

    The number of `OutputPort`s for a particular `OutputPortType` must be within the
    associated `OutputPortType.minimum` and `OutputPortType.maximum` values.

    **Fields**

    - `uuid`
    - `workflow_job` -- a foreign key reference to the associated `WorkflowJob`.
    - `output_port_type` -- a foreign key reference to associated `OutputPortType`.
    - `label` -- an optional name unique to the other `OutputPort`s in the `WorkflowJob`
      (only for the user).
    - `extern` -- an automatically set flag to distinguish an exit `OuputPort` in a
      validated `Workflow`. If the `Workflow` is not valid, this field should be
      ignored.

    **Methods**

    - `save` and `delete` -- invalidate the associated `Workflow`.
    - `save` -- set `label` to the name of its associated `OutputPortType` as a
      default value.
    """
    class Meta:
        app_label = 'rodan'
        permissions = (
            ('view_outputport', 'View OutputPort'),
        )

    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    workflow_job = models.ForeignKey('rodan.WorkflowJob', related_name='output_ports', on_delete=models.CASCADE, db_index=True)
    output_port_type = models.ForeignKey('rodan.OutputPortType', on_delete=models.PROTECT, db_index=True)
    label = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    extern = models.BooleanField(default=False, db_index=True)

    def save(self, *args, **kwargs):
        if not self.label:
            self.label = self.output_port_type.name

        # [TODO] not too efficient... consider do the invalidation in db?
        try:
            old = OutputPort.objects.get(pk=self.pk)
        except OutputPort.DoesNotExist:
            old = OutputPort() # empty

        cond1 = self.workflow_job_id != old.workflow_job_id
        cond2 = self.output_port_type_id != old.output_port_type_id

        wf_new_id = self.workflow_job.workflow_id
        wf_original_id = old.workflow_job.workflow_id if old.workflow_job_id else wf_new_id
        super(OutputPort, self).save(*args, **kwargs)
        if cond1 or cond2:
            Workflow.objects.filter(pk__in=list(set([wf_original_id, wf_new_id]))).update(valid=False)

    def delete(self, *args, **kwargs):
        wf_id = self.workflow_job.workflow_id
        super(OutputPort, self).delete(*args, **kwargs)
        Workflow.objects.filter(pk=wf_id).update(valid=False)

    def __unicode__(self):
        return u"<OutputPort {0}>".format(str(self.uuid))
