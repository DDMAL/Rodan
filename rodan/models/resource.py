import os
import mimetypes
import shutil
from django.conf import settings
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
        if self.resource_file:
            return u"<Resource {0}>".format(self.resource_file.name)

    uuid = UUIDField(primary_key=True, auto=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    project = models.ForeignKey('rodan.Project', related_name="resources")
    resource_file = models.FileField(upload_to=upload_path, null=True, max_length=255)
    compat_resource_file = models.FileField(upload_to=compat_path, null=True, blank=True, max_length=255)
    resource_type = models.CharField(max_length=20, null=True, blank=True)
    processed = models.BooleanField(default=False)

    creator = models.ForeignKey(User, related_name="resources", null=True, blank=True)
    origin = models.ForeignKey('rodan.Output', related_name="+", null=True, blank=True)  # no backward reference

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.name:
            self.resource_type = mimetypes.guess_type(self.name, strict=False)[0]
        super(Resource, self).save(*args, **kwargs)
        if not os.path.exists(self.resource_path):
            os.makedirs(self.resource_path)

        if not os.path.exists(self.thumb_path):
            os.makedirs(self.thumb_path)

    def delete(self, *args, **kwargs):
        if os.path.exists(self.resource_path):
            shutil.rmtree(self.resource_path)
        super(Resource, self).delete(*args, **kwargs)

    @property
    def resource_file_path(self):
        if self.resource_file:
            return os.path.dirname(self.resource_file.path)

    @property
    def thumb_path(self):
        return os.path.join(self.resource_path, "thumbnails")

    @property
    def thumb_url(self):
        return os.path.join(settings.MEDIA_URL, os.path.relpath(self.resource_path, settings.MEDIA_ROOT), "thumbnails")

    @property
    def resource_url(self):
        if self.resource_file:
            return os.path.join(settings.MEDIA_URL, os.path.relpath(self.resource_file.path, settings.MEDIA_ROOT))

    @property
    def compat_file_url(self):
        if self.compat_resource_file:
            return os.path.join(settings.MEDIA_URL, os.path.relpath(self.compat_resource_file.path, settings.MEDIA_ROOT))

    def thumb_filename(self, size):
        if self.filename:
            name, ext = os.path.splitext(self.filename)
            return "{0}_{1}.{2}".format(name, size, settings.THUMBNAIL_EXT)

    @property
    def filename(self):
        if self.resource_file:
            return os.path.basename(self.resource_file.path)

    @property
    def small_thumb_url(self):
        if self.thumb_url and self.filename:
            return os.path.join(self.thumb_url,
                                self.thumb_filename(size=settings.SMALL_THUMBNAIL))

    @property
    def medium_thumb_url(self):
        if self.thumb_url and self.filename:
            return os.path.join(self.thumb_url,
                                self.thumb_filename(size=settings.MEDIUM_THUMBNAIL))

    @property
    def large_thumb_url(self):
        if self.thumb_url and self.filename:
            return os.path.join(self.thumb_url,
                                self.thumb_filename(size=settings.LARGE_THUMBNAIL))
