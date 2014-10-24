from rest_framework import generics
from rodan.helpers.dbmanagement import resolve_object_from_url
from rodan.models.job import Job
from rodan.serializers.job import JobSerializer
from rodan.models.workflowrun import WorkflowRun


class JobList(generics.ListAPIView):
    """
    Returns a list of all workflows. Does not accept POST requests, since Jobs should be defined and loaded server-side.

    - Supported Query Parameters:
        - `enabled=true`: Filter the list of available jobs by their enabled/disabled status.
        - `workflowrun=$ID`: Filter the list of available jobs for those associated with the provided Workflow Run ID.
    - Methods Supported: GET
    - Permissions: Read-only (public)
    """
    model = Job
    serializer_class = JobSerializer
    paginate_by = None

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        enabled = self.request.QUERY_PARAMS.get('enabled', None)
        workflow_run_url = self.request.QUERY_PARAMS.get('workflowrun', None)
        queryset = Job.objects.all()
        if enabled:
            queryset = queryset.filter(enabled=enabled)
        if workflow_run_url:
            workflow_run_instance = resolve_object_from_url(WorkflowRun, workflow_run_url)
            run_jobs = workflow_run_instance.run_jobs.all()
            jobs = []
            for run_job in run_jobs:
                job_pk = run_job.workflow_job.job.pk
                jobs.append(job_pk)
            queryset = queryset.filter(pk__in=jobs)
        return queryset


class JobDetail(generics.RetrieveAPIView):
    """
    Returns a single instance of a Job. Read-only.
    """
    model = Job
    serializer_class = JobSerializer
