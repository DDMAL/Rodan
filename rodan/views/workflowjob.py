from rest_framework import generics
from rest_framework import permissions

from rodan.models.workflowjob import WorkflowJob
from rodan.serializers.workflowjob import WorkflowJobSerializer


class WorkflowJobList(generics.ListCreateAPIView):
    """
    Returns a list of all workflows jobs. Accepts a POST request with a data body to create a new workflow job. POST requests will return the newly-created workflow job object.

    - Supported Query Parameters:
        - `workflow=$ID`: Retrieve workflow jobs belonging to workflow $ID.
    """
    model = WorkflowJob
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = WorkflowJobSerializer
    paginate_by = None

    def get_queryset(self):
        queryset = WorkflowJob.objects.all()
        workflow = self.request.QUERY_PARAMS.get('workflow', None)

        if workflow:
            queryset = queryset.filter(workflow__uuid=workflow)

        return queryset


class WorkflowJobDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Performs operations on a single workflow job instance.
    """
    model = WorkflowJob
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = WorkflowJobSerializer
