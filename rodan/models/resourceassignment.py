from django.db import models
from django_extensions.db.fields import json
from uuidfield import UUIDField


class ResourceAssignment(models.Model):
    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    input_port = models.ForeignKey('rodan.InputPort')
    resources = models.ManyToManyField('rodan.Resource', related_name='resource_assignments')
    workflow = models.ForeignKey('rodan.Workflow')
    workflow_job = models.ForeignKey('rodan.WorkflowJob', null=True, blank=True)
    misc = json.JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.workflow_job = self.input_port.workflow_job
        super(ResourceAssignment, self).save(*args, **kwargs)
