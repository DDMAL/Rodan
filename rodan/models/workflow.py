from django.db import models
from rodan.models.job import Job
from rodan.models.page import Page
from rodan.models.project import Project
from uuidfield import UUIDField


class Workflow(models.Model):
    uuid = UUIDField(primary_key=True, auto=True)
    name = models.CharField(max_length=255)
    project = models.ForeignKey(Project, related_name="workflows")
    jobs = models.ManyToManyField(Job, through='WorkflowJob', null=True, blank=True)
    pages = models.ManyToManyField(Page, related_name="workflows")
    description = models.TextField(blank=True, null=True)
    has_started = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"{0}".format(self.name)

    class Meta:
        app_label = 'rodan'
