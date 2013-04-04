import os
import shutil
from django.db import models
from django.conf import settings
from rodan.models.project import Project
from django.contrib.auth.models import User
from uuidfield import UUIDField


class Page(models.Model):
    @property
    def page_path(self):
        return os.path.join(self.project.project_path, "pages", str(self.uuid))

    def upload_path(self, filename):
        _, ext = os.path.splitext(filename)
        return os.path.join(self.page_path, "original_file{0}".format(ext.lower()))

    def compat_path(self, filename):
        _, ext = os.path.splitext(filename)
        return os.path.join(self.page_path, "compat_file{0}".format(ext.lower()))

    uuid = UUIDField(primary_key=True, auto=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    project = models.ForeignKey(Project, related_name="pages")
    page_image = models.FileField(upload_to=upload_path, null=True, max_length=255)
    compat_page_image = models.FileField(upload_to=compat_path, null=True, blank=True, max_length=255)
    page_order = models.IntegerField(null=True, blank=True)
    processed = models.BooleanField(default=False)

    creator = models.ForeignKey(User, related_name="pages", null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super(Page, self).save(*args, **kwargs)
        if not os.path.exists(self.page_path):
            os.makedirs(self.page_path)

        if not os.path.exists(self.thumb_path):
            os.makedirs(self.thumb_path)

    def delete(self, *args, **kwargs):
        if os.path.exists(self.image_path):
            shutil.rmtree(self.image_path)
        super(Page, self).delete(*args, **kwargs)

    class Meta:
        app_label = 'rodan'

    def __unicode__(self):
        return u"<Page {0}>".format(self.page_image.name)

    def thumb_filename(self, size):
        name, ext = os.path.splitext(self.filename)
        return "{0}_{1}.{2}".format(name, size, settings.THUMBNAIL_EXT)

    @property
    def image_file_size(self):
        if self.page_image:
            return self.page_image.size
        return None

    @property
    def compat_image_file_size(self):
        if self.compat_page_image:
            return self.compat_page_image.size
        return None

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
        return "/" + os.path.relpath(os.path.dirname(self.page_image.url), settings.PROJECT_DIR)

    @property
    def filename(self):
        return os.path.basename(self.page_image.path)

    @property
    def compat_file_path(self):
        return self.compat_page_image.path

    @property
    def compat_file_url(self):
        return self.compat_page_image.url

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
