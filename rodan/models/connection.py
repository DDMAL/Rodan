from django.db import models
from uuidfield import UUIDField


class Connection(models.Model):
    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    input_port = models.ForeignKey('rodan.InputPort')
    output_port = models.ForeignKey('rodan.OutputPort')

    @property
    def input_workflow_job(self):
        return self.input_port.workflow_job

    @property
    def output_workflow_job(self):
        return self.output_port.workflow_job

    @property
    def workflow(self):
        return self.output_port.workflow_job.workflow

    def __unicode__(self):
        return u"<Connection {0}>".format(str(self.uuid))
