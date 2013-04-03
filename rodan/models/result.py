import os
from django.db import models
from uuidfield import UUIDField


class Result(models.Model):
    @property
    def result_path(self):
        return os.path.join(self.run_job.runjob_path)

    def upload_fn(self, filename):
        _, ext = os.path.splitext(os.path.basename(filename))
        return os.path.join(self.result_path, "{0}{1}".format(str(self.uuid), ext))

    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    result = models.FileField(upload_to=upload_fn, null=True, blank=True, max_length=512)
    run_job = models.ForeignKey("rodan.RunJob")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"<Result Hello {0}>".format(self.run_job.workflow_job.job.job_name)

    # def delete(self, *args, **kwargs):
    #     self.result.delete()
    #     super(Result, self).delete(*args, **kwargs)
