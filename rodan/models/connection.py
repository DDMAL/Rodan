from django.db import models
from uuidfield import UUIDField


class Connection(models.Model):
    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    input_port = models.ForeignKey('rodan.InputPort', related_name='connections')
    output_port = models.ForeignKey('rodan.OutputPort', related_name='connections')

    @property
    def input_workflow_job(self):
        return self.input_port.workflow_job

    @property
    def output_workflow_job(self):
        return self.output_port.workflow_job

    @property
    def workflow(self):
        return self.output_port.workflow_job.workflow


    def save(self, *args, **kwargs):
        super(Connection, self).save(*args, **kwargs)
        wf = self.workflow
        if wf.valid:
            wf.valid = False
            wf.save(update_fields=['valid'])

    def delete(self, *args, **kwargs):
        wf = self.workflow
        super(Connection, self).delete(*args, **kwargs)
        if wf.valid:
            wf.valid = False
            wf.save(update_fields=['valid'])

    def __unicode__(self):
        return u"<Connection {0}>".format(str(self.uuid))
