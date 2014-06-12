from django.db import models
from uuidfield import UUIDField


class Output(models.Model):
    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    output_port = models.ForeignKey('rodan.OutputPort')
    run_job = models.ForeignKey('rodan.RunJob', null=True, blank=True)
    resource = models.ForeignKey('rodan.Resource', null=True, blank=True)
