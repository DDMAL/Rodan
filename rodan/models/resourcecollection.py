from django.db import models
from uuidfield import UUIDField
from django.db.models.signals import m2m_changed

class ResourceCollection(models.Model):
    """
    Describes a collection of `Resource`s in a `Workflow`. All `Resource`s should be in
    the same `Project` of the `Workflow`. (Validation implemented in serializer)

    **Fields**

    - `uuid`
    - `resources` -- a many-to-many field referencing `Resource`s.
    - `workflow` -- a reference to the specific `Workflow`.

    **Methods**

    - `resources.add`, `resource.remove` and `resource.clear` -- invalidate the
      associated `Workflow`.
    """
    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    resources = models.ManyToManyField('rodan.Resource', related_name='resource_collections', blank=True, null=True)
    workflow = models.ForeignKey('rodan.Workflow', related_name='resource_collections')


# Invalidate the workflow if ResourceCollection.resources changed.
def _invalidate_workflow_on_resources_change(sender, **kwargs):
    action = kwargs['action']
    if action in ('post_add', 'post_remove', 'post_clear'):
        rc = kwargs['instance']
        wf = rc.workflow
        if wf.valid:
            wf.valid = False
            wf.save(update_fields=['valid'])

m2m_changed.connect(_invalidate_workflow_on_resources_change, sender=ResourceCollection.resources.through)
