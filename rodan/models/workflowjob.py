from django.db import models
from rodan.models.job import Job
from rodan.models.workflow import Workflow
from django_extensions.db.fields import json
from uuidfield import UUIDField


class WorkflowJob(models.Model):
    """ A WorkflowJob is an instantiation of a Job in a Workflow """
    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    workflow = models.ForeignKey(Workflow)
    job = models.ForeignKey(Job)
    sequence = models.IntegerField()
    job_settings = json.JSONField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "%s in workflow '%s' (step %d)" % (self.job, self.workflow, self.sequence)

# this is here because it will be the last thing loaded when we launch
# the django app. Ideally we'll use signals for startup/shutdown, but
# this is not quite ready yet.
# from rodan import jobs
