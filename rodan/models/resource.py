import os
from django.db import models
from django.contrib.auth.models import User
from uuidfield import UUIDField
from rodan.settings import IMAGE_TYPES


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

    RESOURCE_TYPE_CHOICES = (
        ('Images', (
                (IMAGE_TYPES[0], 'Onebit PNG Image'),
                (IMAGE_TYPES[1], 'Greyscale PNG Image'),
                (IMAGE_TYPES[2], 'Grey16 PNG Image'),
                (IMAGE_TYPES[3], 'Colour PNG Image'),
                (IMAGE_TYPES[4], 'Float Image Type'),
                (IMAGE_TYPES[5], 'Complex Image Type'),
            )
        ),
        ('Classifiers', (
        # some classifier types will go here
                (),
            )
        ),
    )

    @property
    def resource_path(self):
        return os.path.join(self.project.project_path, "resources", str(self.uuid))

    uuid = UUIDField(primary_key=True, auto=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    project = models.ForeignKey('rodan.Project', related_name="resources")
    resource_file = models.FileField(upload_to=upload_path, null=True, max_length=255)
    compat_resource_file = models.FileField(upload_to=compat_path, null=True, blank=True, max_length=255)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES)

    creator = models.ForeignKey(User, related_name="resources", null=True, blank=True)
    origin = models.ForeignKey('rodan.Output', related_name="+", null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
