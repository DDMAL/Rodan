from django.db import models
from django_extensions.db.fields import json
from uuidfield import UUIDField


class Connection(models.Model):
    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    input_port = models.ForeignKey('rodan.InputPort')
    input_workflow_job = models.ForeignKey('rodan.WorkflowJob', related_name='input_connection')
    output_port = models.ForeignKey('rodan.OutputPort')
    output_workflow_job = models.ForeignKey('rodan.WorkflowJob', related_name='output_connection')
    workflow = models.ForeignKey('rodan.Workflow', null=True, blank=True)
    misc = json.JSONField()

    def save(self, *args, **kwargs):
        self.workflow = self.output_workflow_job.workflow
        super(Connection, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"<Connection {0}>".format(str(self.uuid))
