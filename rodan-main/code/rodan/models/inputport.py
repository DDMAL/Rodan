from django.db import models
import uuid
from rodan.models.workflow import Workflow
from sortedm2m.fields import SortedManyToManyField


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
    """

    class Meta:
        app_label = "rodan"
        permissions = (("view_inputport", "View InputPort"),)
        ordering = ["created"]

    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    workflow_job = models.ForeignKey(
        "rodan.WorkflowJob",
        related_name="input_ports",
        on_delete=models.CASCADE,
        db_index=True,
    )
    input_port_type = models.ForeignKey(
        "rodan.InputPortType", on_delete=models.CASCADE, db_index=True
    )
    label = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    extern = models.BooleanField(default=False, db_index=True)
    extern_resources = SortedManyToManyField("rodan.Resource", blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.label:
            self.label = self.input_port_type.name

        # [TODO] not too efficient... consider do the invalidation in db?
        try:
            old = InputPort.objects.get(pk=self.pk)
        except InputPort.DoesNotExist:
            old = InputPort()  # empty

        cond1 = self.workflow_job_id != old.workflow_job_id
        cond2 = self.input_port_type_id != old.input_port_type_id

        wf_new_id = self.workflow_job.workflow_id
        wf_original_id = (
            old.workflow_job.workflow_id if old.workflow_job_id else wf_new_id
        )
        super(InputPort, self).save(*args, **kwargs)
        if cond1 or cond2:
            Workflow.objects.filter(
                pk__in=list(set([wf_original_id, wf_new_id]))
            ).update(valid=False)

    def delete(self, *args, **kwargs):
        wf_id = self.workflow_job.workflow_id
        super(InputPort, self).delete(*args, **kwargs)
        Workflow.objects.filter(pk=wf_id).update(valid=False)

    def __str__(self):
        return "<InputPort {0}>".format(str(self.uuid))
