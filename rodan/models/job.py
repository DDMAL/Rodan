from django.db import models
from django_extensions.db.fields import json
from rodan.models.inputporttype import InputPortType
from rodan.models.outputporttype import OutputPortType
from uuidfield import UUIDField


class Job(models.Model):
    """
        A Job represents a task that may be placed in a workflow. When a job is placed
        in a workflow, some of the fields are copied over into a `WorkflowJob`. When a
        workflow is run, these workflowjobs are "frozen" as RunJobs, so that previous runs
        of a workflow may be viewed.

        When Rodan starts up, any jobs defined in the jobs/ directory are loaded into the database
        using this model. All jobs must conform to the same "protocol;" that is, they must define:

        1. input_types: The pixel types for images that may be processed by this job.
        2. output_types: The pixel types that may be produced by this job.
        3. settings: An array of settings that, at a minimum conform to the following structure:
            {
                default: "-1.0",          The default value of the setting. Also used as the runtime value.
                has_default: true,        Whether this has a default value or not. Settings that accept numeric arguments usually have a default.
                name: "noise_variance",   The setting's name. Used both for display, as well as the keyword argument.
                type: "real"              The value type. Could be "real" or "int", etc...
            }

        Interactive jobs must have an interface defined for the interactive part.

        Additionally, a job must define its Category, which is used to group and organize the jobs in the
        Gamera interface. Optionally, a `description` field may give documentation about the job, and an `author`
        can give information about who was responsible for writing the job.

        More information about jobs and their execution may be found in the __init__.py of the jobs/ directory.
    """
    uuid = UUIDField(primary_key=True, auto=True)
    job_name = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    settings = json.JSONField(blank=True, null=True)

    enabled = models.BooleanField(default=False)
    interactive = models.BooleanField(default=False)

    def __unicode__(self):
        return u"<Job {0}>".format(self.job_name)

    class Meta:
        app_label = 'rodan'
        ordering = ['category']

    @property
    def input_port_types(self):
        types = []
        for ipt in InputPortType.objects.filter(job=self):
            types.append(ipt)
        return types

    @property
    def output_port_types(self):
        types = []
        for opt in OutputPortType.objects.filter(job=self):
            types.append(opt)
        return types
