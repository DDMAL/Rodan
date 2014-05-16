import os
import shutil
from django.db import models
from django.conf import settings
from rodan.models.project import Project
from django.contrib.auth.models import User
from uuidfield import UUIDField


def upload_path(instance, filename):
    _, ext = os.path.splitext(filename)
    return os.path.join(instance.page_path, "original_file{0}".format(ext.lower()))

def compat_path(instance, filename):
    _, ext = os.path.splitext(filename)
    return os.path.join(instance.page_path, "compat_file{0}".format(ext.lower()))


class Page(models.Model):
    """
        A Page represents a single page image from a book. When pages are uploaded they are
        automatically sent through a series of Celery tasks (defined in the `helpers` directory)
        that prepare them for Rodan.

        These tasks include:
        1. Make a "compat" image. Compat images are *always* lossless PNG. Image operations are never
            performed on the original file, but on the compat image. This means that any jobs that must be run
            should either operate on PNG images, or contain a (lossless) conversion step. Results should always
            be stored as PNG as well.

        2. Thumbnail. Each page image is thumbnailed for display in three configurable sizes (150, 400, 1000 pixels
            in the largest dimension).

        3. Once 1 & 2 are completed, step 3 simply sets the "processed" flag to True to make Rodan aware that
            the page has gone through these steps.
    """
    @property
    def page_path(self):
        return os.path.join(self.project.project_path, "pages", str(self.uuid))

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
        if os.path.exists(self.page_path):
            shutil.rmtree(self.page_path)
        super(Page, self).delete(*args, **kwargs)

    class Meta:
        app_label = 'rodan'
        ordering = ('page_order',)

    def __unicode__(self):
        if self.page_image:
            return u"<Page {0}>".format(self.page_image.name)

    @property
    def username(self):
        return self.creator.username

    def thumb_filename(self, size):
        if self.filename:
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
        return os.path.join(self.page_path, "thumbnails")

    @property
    def thumb_url(self):
        return os.path.join(settings.MEDIA_URL, os.path.relpath(self.page_path, settings.MEDIA_ROOT), "thumbnails")

    @property
    def image_path(self):
        if self.page_image:
            return os.path.dirname(self.page_image.path)

    @property
    def image_url(self):
        if self.page_image:
            return os.path.join(settings.MEDIA_URL, os.path.relpath(self.page_image.url, settings.MEDIA_ROOT))

    @property
    def filename(self):
        if self.page_image:
            return os.path.basename(self.page_image.path)

    @property
    def compat_file_path(self):
        if self.compat_page_image:
            return self.compat_page_image.path

    @property
    def compat_file_url(self):
        if self.compat_page_image:
            return os.path.join(settings.MEDIA_URL, os.path.relpath(self.compat_page_image.url, settings.MEDIA_ROOT))

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
