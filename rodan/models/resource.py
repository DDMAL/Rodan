import os
import mimetypes
from django.db import models
from django.contrib.auth.models import User
from uuidfield import UUIDField


def upload_path(resource, filename):
    _, ext = os.path.splitext(filename)
    return os.path.join(resource.resource_path, "original_file{0}".format(ext.lower()))


def compat_path(resource, filename):
    _, ext = os.path.splitext(filename)
    return os.path.join(resource.resource_path, "compat_file{0}".format(ext.lower()))


class Resource(models.Model):
    class Meta:
        app_label = 'rodan'

    """
        A Resource is any file associated with a Rodan Project. In the past, Resources were simply
        Pages. However, now it is possible to use any data resource and label it of being a
        specific type. This constitutes a Resource. (from Rodan wiki)
    """

    @property
    def resource_path(self):
        return os.path.join(self.project.project_path, "resources", str(self.uuid))

    def __unicode__(self):
        return u"<Resource {0}>".format(str(self.uuid))

    uuid = UUIDField(primary_key=True, auto=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    project = models.ForeignKey('rodan.Project', related_name="resources")
    resource_file = models.FileField(upload_to=upload_path, null=True, max_length=255)
    compat_resource_file = models.FileField(upload_to=compat_path, null=True, blank=True, max_length=255)
    resource_type = models.CharField(max_length=20)
    run_job = models.ForeignKey('rodan.RunJob', null=True, blank=True)
    workflow = models.ForeignKey('rodan.Workflow', null=True, blank=True)
    processed = models.BooleanField(default=False)

    creator = models.ForeignKey(User, related_name="resources", null=True, blank=True)
    origin = models.ForeignKey('rodan.Output', related_name="+", null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.name:
            self.resource_type = mimetypes.guess_type(self.name, strict=False)[0]
        super(Resource, self).save(*args, **kwargs)
