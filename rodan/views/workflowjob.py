from rest_framework import generics
from rest_framework import permissions

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
    filter_fields = ('workflow', )
    queryset = WorkflowJob.objects.all() # [TODO] filter according to the user?


class WorkflowJobDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Performs operations on a single WorkflowJob instance.
    """
    model = WorkflowJob
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = WorkflowJobSerializer
    queryset = WorkflowJob.objects.all() # [TODO] filter according to the user?
