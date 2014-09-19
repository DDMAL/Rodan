from django.db import models
from uuidfield import UUIDField
from django.db.models.signals import m2m_changed

class ResourceAssignment(models.Model):
    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    input_port = models.ForeignKey('rodan.InputPort')
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
