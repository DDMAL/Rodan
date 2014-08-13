from django.db import models
from django_extensions.db.fields import json
from uuidfield import UUIDField


class OutputPort(models.Model):
    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    workflow_job = models.ForeignKey('rodan.WorkflowJob')
    output_port_type = models.ForeignKey('rodan.OutputPortType')
    label = models.CharField(max_length=255, null=True, blank=True)
    misc = json.JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.label:
            self.label = self.output_port_type.name
        super(OutputPort, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"<OutputPort {0}>".format(str(self.uuid))
