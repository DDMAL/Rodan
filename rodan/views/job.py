from rest_framework import generics

from rodan.paginators.pagination import PaginationSerializer
from rodan.models.job import Job
from rodan.serializers.job import JobSerializer
from rodan.models import Workflow


class JobList(generics.ListAPIView):
    """
    Returns a list of all Jobs. Does not accept POST requests, since
    Jobs should be defined and loaded server-side.

    #### Parameters
    - `enabled` -- GET-only. Boolean value: True/False.
    - `workflowrun` -- GET-only. UUID of WorkflowRun object.
    """
    model = Job
    serializer_class = JobSerializer
    pagination_serializer_class = PaginationSerializer
    filter_fields = ('enabled', )
    queryset = Job.objects.all()

    def get_queryset(self):
        filter_dict = {}

        if 'workflow_run' in self.request.QUERY_PARAMS:
            wfrun_id = self.request.QUERY_PARAMS['workflow_run']
            wf_id = Workflow.objects.filter(workflow_runs__uuid=wfrun_id).values_list('uuid', flat=True)
            filter_dict['workflow_jobs__workflow__uuid__in'] = wf_id

        return Job.objects.filter(**filter_dict)


class JobDetail(generics.RetrieveAPIView):
    """
    Query a single Job instance.
    """
    model = Job
    serializer_class = JobSerializer
    queryset = Job.objects.all()
