import os
from django.db import models
from django.conf import settings
from uuidfield import UUIDField


class Result(models.Model):
    @property
    def result_path(self):
        return self.run_job.runjob_path

    def upload_fn(self, filename):
        _, ext = os.path.splitext(os.path.basename(filename))
        return os.path.join(self.result_path, "{0}{1}".format(str(self.uuid), ext))

    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    result = models.FileField(upload_to=upload_fn, null=True, blank=True, max_length=512)
    run_job = models.ForeignKey("rodan.RunJob", related_name="result")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"<Result {0}>".format(self.run_job.workflow_job.job.job_name)

    def save(self, *args, **kwargs):
        super(Result, self).save(*args, **kwargs)
        if not os.path.exists(self.thumb_path):
            os.makedirs(self.thumb_path)

    @property
    def page_image(self):
        """ A simple wrapper that makes the create_thumbnails task compatible with this model"""
        return self.result

    @property
    def filename(self):
        if (self.result):
            return os.path.basename(self.result.path)

    def thumb_filename(self, size):
        name, ext = os.path.splitext(self.filename)
        return "{0}_{1}.{2}".format(name, size, settings.THUMBNAIL_EXT)

    @property
    def image_url(self):
        return "/" + os.path.relpath(self.result_path, settings.PROJECT_DIR)

    @property
    def thumb_path(self):
        return os.path.join(self.result_path, "thumbnails")

    @property
    def thumb_url(self):
        return os.path.join(self.image_url, "thumbnails")

    @property
    def small_thumb_url(self):
        return os.path.join(self.thumb_url, self.thumb_filename(size=settings.SMALL_THUMBNAIL))

    @property
    def medium_thumb_url(self):
        return os.path.join(self.thumb_url, self.thumb_filename(size=settings.MEDIUM_THUMBNAIL))

    @property
    def large_thumb_url(self):
        return os.path.join(self.thumb_url, self.thumb_filename(size=settings.LARGE_THUMBNAIL))


    # def delete(self, *args, **kwargs):
    #     self.result.delete()
    #     super(Result, self).delete(*args, **kwargs)
