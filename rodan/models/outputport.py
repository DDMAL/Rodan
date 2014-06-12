from django.db import models
from uuidfield import UUIDField


def default_label(sender, instance, created, **kwargs):
    if not instance.label:
        instance.label = instance.output_port_type.name
        instance.save()


class OutputPort(models.Model):
    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    workflow_job = models.ForeignKey('rodan.WorkflowJob', null=True, blank=True)
    output_port_type = models.ForeignKey('rodan.OutputPortType')
    label = models.CharField(max_length=255, null=True, blank=True)

models.signals.post_save.connect(default_label, sender=OutputPort)
