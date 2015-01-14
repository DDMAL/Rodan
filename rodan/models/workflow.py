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
    """

    uuid = UUIDField(primary_key=True, auto=True)
    name = models.CharField(max_length=100)
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
