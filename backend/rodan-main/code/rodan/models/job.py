from django.db import models
from jsonfield import JSONField
import uuid


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
    - `name` -- unique name that corresponds to a Celery task.
    - `author` -- name of the author who is responsible for the job.
    - `category` -- name of the category, used to group and organize the `Job`s.
    - `description` -- documentation.
    - `enabled`
    - `interactive` -- whether the `Job` has manual phases.
    - `settings` -- description of `Job` settings.
    - `job_queue` -- group of celery workers that can execute this `Job`.

    See also: https://github.com/DDMAL/Rodan/wiki/Introduction-to-job-modules
    """

    class Meta:
        app_label = "rodan"

    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    # make sure runjob directory name not exceed 255 characters
    # (Ref: rodan.models.runjob.runjob_path)
    name = models.CharField(max_length=200, unique=True, db_index=True)
    author = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    category = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    description = models.TextField(blank=True, null=True)

    settings = JSONField(default={"type": "object"})

    # Do not manually change this field, it will get overwritten again after every django
    # makemigrations/migrate. Job queues are defined in the RodanJob Class's Settings
    # schema for any specific job, otherwise it will take the default route.
    job_queue = models.CharField(max_length=15, default="celery")

    enabled = models.BooleanField(default=False, db_index=True)
    interactive = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return "<Job {0}>".format(self.name)
