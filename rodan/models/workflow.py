import os
import shutil
from django.db import models
from uuidfield import UUIDField
from django_extensions.db.fields import json


class Workflow(models.Model):
    """
        A Workflow is a sequence of jobs, where the output of one job becomes the input
        of the subsequent job. Each workflow also has multiple Pages assigned to it, so that
        a workflow may apply the same sequence of jobs to all the pages.

        This model uses quoted relationed model names to avoid circular imports.
    """
    @property
    def workflow_path(self):
        return os.path.join(self.project.project_path, "workflows", str(self.uuid))

    uuid = UUIDField(primary_key=True, auto=True)
    name = models.CharField(max_length=255)
    project = models.ForeignKey("rodan.Project", related_name="workflows")
    description = models.TextField(blank=True, null=True)
    has_started = models.BooleanField(default=False)
    runs = models.IntegerField(default=1)
    creator = models.ForeignKey("auth.User", related_name="workflows")
    valid = models.BooleanField(default=False)
    misc = json.JSONField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"<Workflow {0}>".format(self.name)

    class Meta:
        app_label = 'rodan'
        ordering = ('created',)

    def save(self, *args, **kwargs):
        if not self.valid:
            self.valid = False
        super(Workflow, self).save(*args, **kwargs)
        if not os.path.exists(self.workflow_path):
            os.makedirs(self.workflow_path)

    def delete(self, *args, **kwargs):
        if os.path.exists(self.workflow_path):
            shutil.rmtree(self.workflow_path)
        super(Workflow, self).delete(*args, **kwargs)
