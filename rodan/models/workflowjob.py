from django.db import models
from rodan.models.job import Job
from rodan.models.workflow import Workflow
from rodan.models.inputport import InputPort
from rodan.models.outputport import OutputPort
from django_extensions.db.fields import json
from uuidfield import UUIDField


class WorkflowJob(models.Model):
    """
        A WorkflowJob is a Job object that has been added to a workflow.

        WorkflowJobs may be interactive or non-interactive. An interactive job will present
        users with an interface for performing a unit of work; for example, cropping or rotating a page,
        or confirming an operation before the image can proceed to the next job.

        Non-interactive jobs do not require human input (e.g., converting an RGB image to greyscale) and
        as such may be executed automatically.
    """
    WORKFLOW_JOB_TYPES = (
        (0, "Non-Interactive"),
        (1, "Interactive")
    )

    uuid = UUIDField(primary_key=True, auto=True)
    workflow = models.ForeignKey(Workflow, related_name="workflow_jobs", blank=True, null=True)
    job = models.ForeignKey(Job)
    job_type = models.IntegerField(choices=WORKFLOW_JOB_TYPES, default=0)
    job_settings = json.JSONField(default="[]", blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"<WorkflowJob {0}>".format(str(self.uuid))

    class Meta:
        app_label = 'rodan'

    @property
    def job_name(self):
        return self.job.job_name

    @property
    def job_description(self):
        return self.job.description

    @property
    def input_ports(self):
        return [ip for ip in InputPort.objects.filter(workflow_job=self)]

    @property
    def output_ports(self):
        return [op for op in OutputPort.objects.filter(workflow_job=self)]


# class WorkflowJob(models.Model):
#     """ A WorkflowJob is an instantiation of a Job in a Workflow """
#     class Meta:
#         app_label = 'rodan'
#         ordering = ['sequence']

#     WORKFLOW_JOB_TYPES = (
#         (0, "Non-Interactive"),
#         (1, "Interactive")
#     )

#     uuid = UUIDField(primary_key=True, auto=True)
#     workflow = models.ForeignKey(Workflow, related_name="wjobs")
#     job = models.ForeignKey(Job)

#     workflow_run = models.IntegerField(blank=True, null=True, default=1)
#     sequence = models.IntegerField(blank=True, null=True)

#     job_settings = json.JSONField(blank=True, null=True)
#     # job_settings = models.ManyToManyField(WorkflowJobSetting)
#     job_type = models.IntegerField(choices=WORKFLOW_JOB_TYPES, default=0)

#     # for interactive jobs: If this is set to True the job will not run.
#     # set it to false to allow it to run.
#     needs_input = models.BooleanField(default=False)
#     page = models.ForeignKey(Page, blank=True, null=True)

#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)

#     def __unicode__(self):
#         # return "%s in workflow '%s' (step %d)" % (self.job, self.workflow, self.sequence)
#         return u"{0} ({1})".format(self.job, self.get_job_type_display())

#     @property
#     def job_name(self):
#         return self.job.job_name

#     @property
#     def job_description(self):
#         return self.job.description

#     @property
#     def input_pixel_types(self):
#         return self.job.input_types["pixel_types"]

#     @property
#     def output_pixel_types(self):
#         return self.job.output_types["pixel_types"]

# this is here because it will be the last thing loaded when we launch
# the django app. Ideally we'll use signals for startup/shutdown, but
# this is not quite ready yet.
# from rodan import jobs
