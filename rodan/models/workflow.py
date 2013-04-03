import os
import shutil
from django.db import models
from uuidfield import UUIDField


class Workflow(models.Model):
    """
        This model uses quoted relationship names to avoid
        circular imports.
    """
    @property
    def workflow_path(self):
        return os.path.join(self.project.project_path, "workflows", str(self.uuid))

    uuid = UUIDField(primary_key=True, auto=True)
    name = models.CharField(max_length=255)
    project = models.ForeignKey("rodan.Project", related_name="workflows")
    pages = models.ManyToManyField("rodan.Page", related_name="workflows", blank=True)
    description = models.TextField(blank=True, null=True)
    has_started = models.BooleanField(default=False)
    runs = models.IntegerField(default=1)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"<Workflow {0}>".format(self.name)

    class Meta:
        app_label = 'rodan'

    def save(self, *args, **kwargs):
        super(Workflow, self).save(*args, **kwargs)
        if not os.path.exists(self.workflow_path):
            os.makedirs(self.workflow_path)

    def delete(self, *args, **kwargs):
        if os.path.exists(self.workflow_path):
            shutil.rmtree(self.workflow_path)
        super(Workflow, self).delete(*args, **kwargs)
