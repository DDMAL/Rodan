import os
from django.db import models
from django.conf import settings
from uuidfield import UUIDField
from rodan.settings import IMAGE_TYPES


def upload_fn(instance, filename):
    _, ext = os.path.splitext(os.path.basename(filename))
    return os.path.join(instance.result_path, "{0}{1}".format(str(instance.uuid), ext))


class Result(models.Model):
    """
        A Result object stores pointers to the output of a RunJob. A single result file is the output
        of the job, but like Pages, a result is *always* thumbnailed for display on the interface.

    """
    @property
    def result_path(self):
        return self.run_job.runjob_path

    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    result = models.FileField(upload_to=upload_fn, null=True, blank=True, max_length=512)
    run_job = models.ForeignKey("rodan.RunJob", related_name="result")
    processed = models.BooleanField(default=False)

    # For now, for the sake of backwards compatibility, None/null should just mean a regular png image.
    result_type = models.IntegerField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"<Result {0}>".format(self.run_job.workflow_job.job.job_name)

    def save(self, *args, **kwargs):
        super(Result, self).save(*args, **kwargs)
        if self.result_type in IMAGE_TYPES and not os.path.exists(self.thumb_path):
            os.makedirs(self.thumb_path)
        self.run_job.save()

    @property
    def run_job_name(self):
        return self.run_job.job_name

    @property
    def page_image(self):
        """ A simple wrapper that makes the create_thumbnails task compatible with this model"""
        return self.result

    @property
    def filename(self):
        if self.result:
            return os.path.basename(self.result.path)

    def thumb_filename(self, size):
        name, ext = os.path.splitext(self.filename)
        return "{0}_{1}.{2}".format(name, size, settings.THUMBNAIL_EXT)

    @property
    def image_url(self):
        if self.result:
            return os.path.join(settings.MEDIA_URL, os.path.relpath(self.result.path, settings.MEDIA_ROOT))

    @property
    def thumb_path(self):
        return os.path.join(self.result_path, "thumbnails")

    @property
    def thumb_url(self):
        if self.result:
            return os.path.join(settings.MEDIA_URL, os.path.relpath(self.result_path, settings.MEDIA_ROOT), "thumbnails")

    @property
    def small_thumb_url(self):
        if self.result:
            return os.path.join(self.thumb_url, self.thumb_filename(size=settings.SMALL_THUMBNAIL))

    @property
    def medium_thumb_url(self):
        if self.result:
            return os.path.join(self.thumb_url, self.thumb_filename(size=settings.MEDIUM_THUMBNAIL))

    @property
    def large_thumb_url(self):
        if self.result:
            return os.path.join(self.thumb_url, self.thumb_filename(size=settings.LARGE_THUMBNAIL))

    # def delete(self, *args, **kwargs):
    #     self.result.delete()
    #     super(Result, self).delete(*args, **kwargs)
