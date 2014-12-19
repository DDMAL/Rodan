from django.db import models
from uuidfield import UUIDField

class ResourceAssignment(models.Model):
    """
    Describes the assignment of a `Resource` *or* a `ResourceCollection` to an `InputPort`.

    The `InputPort` and `ResourceCollection` should be in the same `Workflow`, if a
    `ResourceCollection` is assigned. Otherwise, the `InputPort` and `Resource` should
    be in the same `Project`. (Validation implemented in serializer)

    **Fields**

    - `uuid`
    - `input_port` -- a reference to the specific `InputPort`.

    - `resource` -- a reference to the specific `Resource`.
    - `resource_collection` -- a reference to the specific `ResourceCollection`.

    **Properties**

    - `workflow` -- the `Workflow` instance which the `ResourceAssignment` is a part of.
    - `workflow_job` -- the `WorkflowJob` instance that the `InputPort` is on.

    **Methods**

    - `save` and `delete` -- invalidate the associated `Workflow`.
    """
    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    input_port = models.ForeignKey('rodan.InputPort', related_name='resource_assignments')

    resource = models.ForeignKey('rodan.Resource', related_name='resource_assignments', blank=True, null=True)
    resource_collection = models.ForeignKey('rodan.ResourceCollection', related_name='resource_assignments', blank=True, null=True)

    @property
    def workflow(self):
        return self.input_port.workflow_job.workflow

    @property
    def workflow_job(self):
        return self.input_port.workflow_job

    def save(self, *args, **kwargs):
        super(ResourceAssignment, self).save(*args, **kwargs)
        wf = self.workflow
        if wf.valid:
            wf.valid = False
            wf.save()

    def delete(self, *args, **kwargs):
        wf = self.workflow
        super(ResourceAssignment, self).delete(*args, **kwargs)
        if wf.valid:
            wf.valid = False
            wf.save()
