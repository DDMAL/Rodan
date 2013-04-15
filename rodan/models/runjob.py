import os
import shutil
from django.db import models
from django_extensions.db.fields import json
from uuidfield import UUIDField
# from rodan.models.job import Job
# from rodan.models.result import Result


class RunJob(models.Model):
    @property
    def runjob_path(self):
        return os.path.join(self.workflow_run.workflow_run_path, "{0}_{1}".format(self.workflow_job.sequence, str(self.pk)))

    class Meta:
        app_label = 'rodan'
        ordering = ['workflow_job__sequence']

    uuid = UUIDField(primary_key=True, auto=True)
    workflow_run = models.ForeignKey("rodan.WorkflowRun", related_name="run_jobs")
    workflow_job = models.ForeignKey("rodan.WorkflowJob")
    page = models.ForeignKey("rodan.Page")

    job_settings = json.JSONField(blank=True, null=True)
    needs_input = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"<RunJob {0} {1} ({2})>".format(str(self.uuid), self.workflow_job.job.job_name, self.needs_input)

    def save(self, *args, **kwargs):
        super(RunJob, self).save(*args, **kwargs)
        if not os.path.exists(self.runjob_path):
            os.makedirs(self.runjob_path)

    def delete(self, *args, **kwargs):
        if os.path.exists(self.runjob_path):
            shutil.rmtree(self.runjob_path)
        super(RunJob, self).delete(*args, **kwargs)

    @property
    def sequence(self):
        return self.workflow_job.sequence

    @property
    def job_name(self):
        return self.workflow_job.job_name

    @property
    def page_name(self):
        return self.page.name
