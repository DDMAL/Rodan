from rest_framework import generics
from rest_framework import permissions

from rodan.models.workflowjob import WorkflowJob
from rodan.serializers.workflowjob import WorkflowJobSerializer


class WorkflowJobList(generics.ListCreateAPIView):
    model = WorkflowJob
    serializer_class = WorkflowJobSerializer


class WorkflowJobDetail(generics.RetrieveUpdateDestroyAPIView):
    model = WorkflowJob
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    serializer_class = WorkflowJobSerializer
