import os
import shutil
from django.db import models
from uuidfield import UUIDField
from django.apps import apps

class Workflow(models.Model):
    """
    A `Workflow` is a container of jobs and their connections.

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

    - `workflow_input_ports` -- if the `Workflow` is valid, returns all `InputPorts`
      with extern=True. If the `Workflow` is not valid, returns empty list.
    - `workflow_output_ports` -- if the `Workflow` is valid, returns all `OutputPorts`
      with extern=True. If the `Workflow` is not valid, returns empty list.
    """

    uuid = UUIDField(primary_key=True, auto=True)
    name = models.CharField(max_length=100)
    project = models.ForeignKey("rodan.Project", related_name="workflows", on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    creator = models.ForeignKey("auth.User", related_name="workflows", null=True, blank=True, on_delete=models.SET_NULL)
    valid = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"<Workflow {0}>".format(self.name)

    class Meta:
        app_label = 'rodan'
        ordering = ('created',)

    @property
    def workflow_input_ports(self):
        if not self.valid:
            return []
        else:
            return apps.get_model(app_label='rodan', model_name='InputPort').objects.filter(workflow_job__workflow=self, extern=True)

    @property
    def workflow_output_ports(self):
        if not self.valid:
            return []
        else:
            return apps.get_model(app_label='rodan', model_name='OutputPort').objects.filter(workflow_job__workflow=self, extern=True)
