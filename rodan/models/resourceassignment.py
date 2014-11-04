from django.db import models
from uuidfield import UUIDField
from django.db.models.signals import m2m_changed

class ResourceAssignment(models.Model):
    """
    Describes the assignment of `Resource`s to an `InputPort`.

    **Fields**

    - `uuid`
    - `input_port` -- a reference to the specific `InputPort`.
    - `resources` -- a many-to-many field referencing zero or more `Resource`s.
      the "output" end of the connection.

    **Properties**

    - `workflow` -- the `Workflow` instance which the `ResourceAssignment` is a part of.
    - `workflow_job` -- the `WorkflowJob` instance that the `InputPort` is on.

    **Methods**

    - `save` and `delete` -- invalidate the associated `Workflow`.
    - `resources.add`, `resource.remove` and `resource.clear` -- invalidate the
      associated `Workflow`.
    """
    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    input_port = models.ForeignKey('rodan.InputPort', related_name='resource_assignments')
    resources = models.ManyToManyField('rodan.Resource', related_name='resource_assignments')

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
            wf.save(update_fields=['valid'])

    def delete(self, *args, **kwargs):
        wf = self.workflow
        super(ResourceAssignment, self).delete(*args, **kwargs)
        if wf.valid:
            wf.valid = False
            wf.save(update_fields=['valid'])


# Invalidate the workflow if ResourceAssignment.resources changed.
def _invalidate_workflow_on_resources_change(sender, **kwargs):
    action = kwargs['action']
    if action in ('post_add', 'post_remove', 'post_clear'):
        ra = kwargs['instance']
        wf = ra.workflow
        if wf.valid:
            wf.valid = False
            wf.save(update_fields=['valid'])

m2m_changed.connect(_invalidate_workflow_on_resources_change, sender=ResourceAssignment.resources.through)
