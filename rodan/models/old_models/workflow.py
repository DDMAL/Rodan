from django.db import models
from rodan.celery_models.jobtype import JobType


class Workflow(models.Model):
    class Meta:
        app_label = 'rodan'

    project = models.ForeignKey('rodan.Project')
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    jobs = models.ManyToManyField('rodan.Job', through='JobItem', null=True, blank=True)
    has_started = models.BooleanField(default=False)
    pk_name = 'workflow_id'

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('rodan.views.workflows.view', [str(self.id)])

    def get_percent_done(self):
        percent_done = sum(page.get_percent_done() for page in self.page_set.all())
        return percent_done / self.page_set.count() if self.page_set.count() else 0

    def get_workflow_jobs(self):
        """Get all the the job items in a workflow."""
        return [job_item.job for job_item in self.jobitem_set.all()]

    def get_required_jobs(self):
        """
        Return a list of all the jobs with a required flag that are compatible with the last added job
        that can be added (i.e. are not already chosen).
        """
        Job = models.get_model('rodan', 'Job')
        workflow_jobs = self.get_workflow_jobs()
        if workflow_jobs:
            last_job = self.get_workflow_jobs()[-1]
            return [job for job in Job.objects.filter(is_required=True) if job not in self.get_workflow_jobs() and last_job.is_compatible(job)]
        else:
            return [job for job in Job.objects.filter(is_required=True) if job not in self.get_workflow_jobs() and job.get_object().input_type == JobType.IMAGE]

    def has_required_compatibility(self, job):
        """
        Check that the arguement job is compatible with all required jobs in this step.
        i.e., has the same output type as all the input types of the required jobs at the current step.
        """
        return all(job.is_compatible(req_job) for req_job in self.get_required_jobs())

    def get_available_jobs(self):
        """
        Return a list of the available jobs to choose from when creating a workflow,
        checks that all required jobs are added before moving to a different input type.
        """
        Job = models.get_model('rodan', 'Job')

        available_jobs = []
        workflow_jobs = self.get_workflow_jobs()
        required_jobs = self.get_required_jobs()
        if workflow_jobs:
            last_job = workflow_jobs[-1]
            #First finds enabled jobs that aren't required
            available_jobs = [job for job in Job.objects.filter(enabled=True, is_required=False) if job not in workflow_jobs and last_job.is_compatible(job)]
            #If there are required jobs, filters out those jobs not compatible with required jobs, else returns available jobs
            if required_jobs:
                available_jobs = required_jobs + [job for job in available_jobs and self.has_required_compatibility(job)]
        else:
            #If there aren't any workflow jobs, finds all enabled jobs that aren't required
            available_jobs = [job for job in Job.objects.filter(enabled=True, is_required=False) if job.get_object().input_type == JobType.IMAGE]
            #If there are required jobs, filters out all jobs that aren't compatible with the required jobs
            if required_jobs:
                available_jobs = required_jobs + [job for job in available_jobs if self.has_required_compatibility(job)]

        return available_jobs

    def get_removable_jobs(self):
        """
        Get all the removeable jobs in a workflow (i.e., jobs with the same input as output type).
        """
        return [job for job in self.get_workflow_jobs() if job.get_object().input_type == job.get_object().output_type]

    def get_jobs_same_io_type(self):
        """
        Get all the jobs in the available_jobs that have the same input_type as output_type.
        """
        return [job for job in self.get_available_jobs() if job.get_object().input_type == job.get_object().output_type]

    def get_jobs_diff_io_type(self):
        return [job for job in self.get_available_jobs() if job.get_object().input_type != job.get_object().output_type]
