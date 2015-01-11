from django.db import models
from jsonfield import JSONField
from uuidfield import UUIDField


class Job(models.Model):
    """
    `Job`s are the "templates" that make up the executable tasks in a `Workflow`.
    `Job`s themselves are not executed. Rather, they are analogous to OOP classes
    in that they have parameters with well-defined ranges and input/output ports.

    (`Job`s are used to create `WorkflowJob`s.  A `WorkflowJob` is an "instance" of
    a `Job` with `Job.settings[]` values set and associated `input_port`s and
    `output_port`s.  These are described later.)

    **Fields**

    - `uuid`
    - `job_name` -- unique name that corresponds to a Celery task.
    - `author` -- name of the author who is responsible for the job.
    - `category` -- name of the category, used to group and organize the `Job`s.
    - `description` -- documentation.
    - `enabled`
    - `interactive` -- whether the `Job` has manual phases.
    - `settings` -- description of `Job` settings.

    See also: https://github.com/DDMAL/Rodan/wiki/Introduction-to-job-modules
    """
    uuid = UUIDField(primary_key=True, auto=True)
    job_name = models.CharField(max_length=200, unique=True)   # make sure runjob directory name not exceed 255 characters (Ref: rodan.models.runjob.runjob_path)
    author = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    settings = JSONField(default={"type": "object"})

    enabled = models.BooleanField(default=False)
    interactive = models.BooleanField(default=False)

    def __unicode__(self):
        return u"<Job {0}>".format(self.job_name)

    class Meta:
        app_label = 'rodan'
