from django.db import models


class Workflow(models.Model):
    name = models.CharField(max_length=255)
    jobs = models.ManyToManyField('rodan.Job', through='WorkflowJob', null=True, blank=True)
    pages = models.ManyToManyField('rodan.Page')
    description = models.TextField()
    has_started = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'rodan'
