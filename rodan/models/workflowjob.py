from django.db import models
from rodan.models.job import Job
from rodan.models.workflow import Workflow


class WorkflowJob(models.Model):
    """ A WorkflowJob is an instantiation of a Job in a Workflow """
    class Meta:
        app_label = 'rodan'

    workflow = models.ForeignKey(Workflow)
    job = models.ForeignKey(Job)
    sequence = models.IntegerField()
    job_settings = models.CharField(max_length=255)  # we will set this to something sane later

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "%s in workflow '%s' (step %d)" % (self.job, self.workflow, self.sequence)
