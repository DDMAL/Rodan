from django.db import models
from django.conf import settings
from rodan.models.project import Project
from django.contrib.auth.models import User
from uuidfield import UUIDField

import os


class Page(models.Model):
    def upload_path(self, filename):
        _, ext = os.path.splitext(filename)
        return os.path.join("projects", str(self.project.uuid), "pages", str(self.uuid), "original_file{0}".format(ext.lower()))

    uuid = UUIDField(primary_key=True, auto=True)
    project = models.ForeignKey(Project, related_name="pages")
    page_image = models.FileField(upload_to=upload_path, null=True)

    # we specify the same upload path, but we'll be replacing it with a converted
    # image later.
    compat_page_image = models.FileField(upload_to=upload_path, null=True)
    page_order = models.IntegerField(null=True)
    image_file_size = models.IntegerField(null=True)  # in bytes
    processed = models.BooleanField(default=False)

    creator = models.ForeignKey(User, related_name="pages", null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'rodan'

    def __unicode__(self):
        return unicode(self.page_image.name)

    def thumb_filename(self, size):
        name, ext = os.path.splitext(self.filename)
        return "{0}_{1}{2}".format(name, size, ext.lower())

    @property
    def thumb_path(self):
        return os.path.join(self.image_path, "thumbnails")

    @property
    def thumb_url(self):
        return os.path.join(self.image_url, "thumbnails")

    @property
    def image_path(self):
        return os.path.dirname(self.page_image.path)

    @property
    def image_url(self):
        return os.path.dirname(self.page_image.url)

    @property
    def filename(self):
        return os.path.basename(self.page_image.path)

    @property
    def small_thumb_url(self):
        return os.path.join(self.thumb_url,
                            self.thumb_filename(size=settings.SMALL_THUMBNAIL))

    @property
    def medium_thumb_url(self):
        return os.path.join(self.thumb_url,
                            self.thumb_filename(size=settings.MEDIUM_THUMBNAIL))

    @property
    def large_thumb_url(self):
        return os.path.join(self.thumb_url,
                            self.thumb_filename(size=settings.LARGE_THUMBNAIL))
