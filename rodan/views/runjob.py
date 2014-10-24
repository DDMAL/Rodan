from rest_framework import generics
from rest_framework import permissions

from rodan.models.runjob import RunJob
from rodan.models.runjob import RunJobStatus
from rodan.serializers.runjob import RunJobSerializer


class RunJobList(generics.ListAPIView):
    """
    Returns a list of all run jobs. Run Jobs are typically created by the server, so this does not accept POST requests.

    - Supported Query Parameters:
        - `requires_interaction=true`: Sets whether only those Run Jobs that currently require interaction will be returned or not (GET only).
        - `project=$ID`: Retrieve runjobs belonging to project $ID (GET only).
        - `workflowrun=$ID`: Retrieve runjobs belonging to workflow run $ID (GET only).
        - `page=$ID`: Retrieve runjobs belonging to page $ID (GET only).
    """
    model = RunJob
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = RunJobSerializer
    paginate_by = None

    def get_queryset(self):
        requires_interaction = self.request.QUERY_PARAMS.get('requires_interaction', None)
        project = self.request.QUERY_PARAMS.get('project', None)
        workflowrun = self.request.QUERY_PARAMS.get('workflowrun', None)
        queryset = RunJob.objects.all()
        if requires_interaction:
            queryset = queryset.filter(needs_input=1).filter(status__in=[RunJobStatus.WAITING_FOR_INPUT, RunJobStatus.RUN_ONCE_WAITING])
        if project:
            queryset = queryset.filter(workflow_job__workflow__project__uuid=project)
        if workflowrun:
            queryset = queryset.filter(workflow_run=workflowrun)

        return queryset


class RunJobDetail(generics.RetrieveAPIView):
    """
    Performs operations on a single Run Job instance. Does not support the DELETE method.
    """
    model = RunJob
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = RunJobSerializer
