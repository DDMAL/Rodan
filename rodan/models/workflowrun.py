import os
from django.db import models
from uuidfield import UUIDField
# from django_extensions.db.fields import json


class WorkflowRun(models.Model):
    """
        A WorkflowRun model represents the running of a workflow. Since Rodan is based
        on a RESTful design, workflows are *not* run by sending a "run workflow" command.
        Rather, they are run by creating a new WorkflowRun resource.

        WorkflowRuns can be either a test run, or a "real" run. Test runs operate on a single page,
        while "real" runs operate on a whole collection of pages.

        Each RunJob instance has a foreign key to the WorkflowRun they are associated with.

        To see how WorkflowRuns are executed, see `views/workflowrun.py`.
    """
    @property
    def workflow_run_path(self):
        return os.path.join(self.workflow.workflow_path, "runs", str(self.pk))

    class Meta:
        app_label = 'rodan'

    uuid = UUIDField(primary_key=True, auto=True)
    workflow = models.ForeignKey('rodan.Workflow', related_name="workflow_runs")
    run = models.IntegerField(null=True, blank=True)
    test_run = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"<WorkflowRun {0}>".format(str(self.uuid))

    def save(self, *args, **kwargs):
        super(WorkflowRun, self).save(*args, **kwargs)
        if not os.path.exists(self.workflow_run_path):
            os.makedirs(self.workflow_run_path)

    def get_absolute_url(self):
        """ NOTE: This is a hack. We should come up with a more flexible way of doing this. """
        return u"/workflowrun/{0}/".format(self.pk)
