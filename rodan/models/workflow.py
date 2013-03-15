from django.db import models
from uuidfield import UUIDField


class Workflow(models.Model):
    """
        This model uses quoted relationship names to avoid
        circular imports.
    """
    uuid = UUIDField(primary_key=True, auto=True)
    name = models.CharField(max_length=255)
    project = models.ForeignKey("rodan.Project", related_name="workflows")
    jobs = models.ManyToManyField("rodan.Job", through='rodan.WorkflowJob', related_name="workflows", blank=True)
    pages = models.ManyToManyField("rodan.Page", related_name="workflows", blank=True)
    description = models.TextField(blank=True, null=True)
    has_started = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"{0}".format(self.name)

    class Meta:
        app_label = 'rodan'

    def next_job(self, wf_job, page):
        """Fetches the next job in the workflow, or None if it is the last job"""
        lookup = self.wjobs.filter(sequence=wf_job.sequence + 1, page=page)
        if lookup:
            # if this doesn't return an empty list, we know there's a next job
            return lookup.get()
        else:
            return None

    def previous_job(self, wf_job, page):
        """Fetches the previous job in the workflow, or None if it is the first job"""
        lookup = self.wjobs.filter(sequence=wf_job.sequence - 1, page=page)
        if lookup:
            return lookup.get()
        else:
            return None
