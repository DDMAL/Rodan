from django.db import models
from uuidfield import UUIDField


class OutputPortType(models.Model):
    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    job = models.ForeignKey('rodan.Job', related_name='output_port_types')
    name = models.CharField(max_length=255)
    resource_types = models.ManyToManyField('rodan.ResourceType', related_name='output_port_types')
    minimum = models.IntegerField()
    maximum = models.IntegerField()

    def __unicode__(self):
        return u"<OutputPortType {0}>".format(str(self.uuid))
