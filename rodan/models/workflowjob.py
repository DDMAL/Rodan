from django.db import models
from rodan.models.job import Job
from rodan.models.page import Page
from rodan.models.workflow import Workflow
from django_extensions.db.fields import json
from uuidfield import UUIDField


class WorkflowJob(models.Model):
    """ A WorkflowJob is an instantiation of a Job in a Workflow """
    class Meta:
        app_label = 'rodan'
        ordering = ['sequence']

    WORKFLOW_JOB_TYPES = (
        (0, "Non-Interactive"),
        (1, "Interactive")
    )

    uuid = UUIDField(primary_key=True, auto=True)
    workflow = models.ForeignKey(Workflow, related_name="wjobs")
    job = models.ForeignKey(Job)
    sequence = models.IntegerField(blank=True, null=True)
    job_settings = json.JSONField(blank=True, null=True)

    job_type = models.IntegerField(choices=WORKFLOW_JOB_TYPES, default=0)

    # for interactive jobs: If this is set to True the job will not run.
    # set it to false to allow it to run.
    needs_input = models.BooleanField(default=False)
    page = models.ForeignKey(Page)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        # return "%s in workflow '%s' (step %d)" % (self.job, self.workflow, self.sequence)
        return u"{0} ({1})".format(self.job, self.get_job_type_display())

    @property
    def name(self):
        return self.job.name

    @property
    def input_pixel_types(self):
        return self.job.input_types["pixel_types"]

    @property
    def output_pixel_types(self):
        return self.job.output_types["pixel_types"]

# this is here because it will be the last thing loaded when we launch
# the django app. Ideally we'll use signals for startup/shutdown, but
# this is not quite ready yet.
# from rodan import jobs
