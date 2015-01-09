from rest_framework import generics
from rest_framework import permissions

from rodan.paginators.pagination import PaginationSerializer
from rodan.models.workflowjob import WorkflowJob
from rodan.serializers.workflowjob import WorkflowJobSerializer


class WorkflowJobList(generics.ListCreateAPIView):
    """
    Returns a list of all WorkflowJobs. Accepts a POST request with a data body
    to create a new WorkflowJob. POST requests will return the newly-created
    WorkflowJob object.

    #### GET Parameters
    - `workflow`
    """
    model = WorkflowJob
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = WorkflowJobSerializer
    pagination_serializer_class = PaginationSerializer
    filter_fields = ('workflow', )
    queryset = WorkflowJob.objects.all() # [TODO] filter according to the user?

    def perform_create(self, serializer):
        if not 'job_settings' in serializer.validated_data:
            j_settings = serializer.validated_data['job'].settings
            s = {}
            for properti, definition in j_settings.get('properties', {}).iteritems():
                if 'default' in definition:
                    s[properti] = definition['default']
            serializer.validated_data['job_settings'] = s
        serializer.save()


class WorkflowJobDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Performs operations on a single WorkflowJob instance.
    """
    model = WorkflowJob
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = WorkflowJobSerializer
    queryset = WorkflowJob.objects.all() # [TODO] filter according to the user?
