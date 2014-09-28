from django.db import models
from django_extensions.db.fields import json
from uuidfield import UUIDField


class InputPortType(models.Model):
    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    job = models.ForeignKey('rodan.Job', null=True, blank=True, related_name='input_port_types')
    name = models.CharField(max_length=255, null=True, blank=True)
    resource_type = json.JSONField()
    minimum = models.IntegerField()
    maximum = models.IntegerField()

    def __unicode__(self):
        return u"<InputPortType {0}>".format(str(self.uuid))
