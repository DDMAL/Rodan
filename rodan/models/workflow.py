import os
import shutil
from django.db import models
from uuidfield import UUIDField


class Workflow(models.Model):
    """
    A `Workflow` is a container of jobs, their connections, and resource assignments.

    **Fields**

    - `uuid`
    - `name`
    - `description`
    - `project` -- a reference to `Project` where it resides.
    - `creator` -- a reference to `User` who created it.
    - `valid` -- a boolean, indicating whether the contents of `Workflow` is valid.
    - `created`
    - `updated`

    **Properties**

    - `workflow_path` [TODO] deprecated: we use resource path now

    **Methods**

    - `save` and `delete` [TODO] deprecated: we use resource path now
    """
    @property
    def workflow_path(self):
        return os.path.join(self.project.project_path, "workflows", str(self.uuid))

    uuid = UUIDField(primary_key=True, auto=True)
    name = models.CharField(max_length=255)
    project = models.ForeignKey("rodan.Project", related_name="workflows")
    description = models.TextField(blank=True, null=True)
    creator = models.ForeignKey("auth.User", related_name="workflows")
    valid = models.BooleanField(default=False)

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
