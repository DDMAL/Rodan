from django.db import models
from uuidfield import UUIDField


class Output(models.Model):
    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    output_port = models.ForeignKey('rodan.OutputPort')
    run_job = models.ForeignKey('rodan.RunJob', related_name='outputs')
    resource = models.ForeignKey('rodan.Resource')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"<Output {0}>".format(str(self.uuid))
