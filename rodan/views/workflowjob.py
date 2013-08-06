from rest_framework import generics
from rest_framework import permissions

from rodan.models.workflowjob import WorkflowJob
from rodan.serializers.workflowjob import WorkflowJobSerializer


class WorkflowJobList(generics.ListCreateAPIView):
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
    model = WorkflowJob
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = WorkflowJobSerializer
