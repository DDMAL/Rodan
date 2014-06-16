from django.db import models
from uuidfield import UUIDField


class ResourceAssignment(models.Model):
    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    input_port = models.ForeignKey('rodan.InputPort')
    resources = models.ManyToManyField('rodan.Resource', related_name='resource_assignments')
    workflow = models.ForeignKey('rodan.Workflow')
