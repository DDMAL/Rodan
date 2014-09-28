from django.db import models
from uuidfield import UUIDField


class InputPort(models.Model):
    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    workflow_job = models.ForeignKey('rodan.WorkflowJob', related_name='input_ports')
    input_port_type = models.ForeignKey('rodan.InputPortType')
    label = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.label:
            self.label = self.input_port_type.name
        super(InputPort, self).save(*args, **kwargs)

        wf = self.workflow_job.workflow
        if wf.valid:
            wf.valid = False
            wf.save(update_fields=['valid'])

    def delete(self, *args, **kwargs):
        wf = self.workflow_job.workflow
        super(InputPort, self).delete(*args, **kwargs)
        if wf.valid:
            wf.valid = False
            wf.save(update_fields=['valid'])

    def __unicode__(self):
        return u"<InputPort {0}>".format(str(self.uuid))
