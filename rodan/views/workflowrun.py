from rest_framework import generics
from rest_framework import permissions

from rodan.models.workflowrun import WorkflowRun
from rodan.serializers.workflowrun import WorkflowRunSerializer


class WorkflowRunList(generics.ListCreateAPIView):
    model = WorkflowRun
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    serializer_class = WorkflowRunSerializer

    def get_queryset(self):
        workflow = self.request.QUERY_PARAMS.get('workflow', None)
        run = self.request.QUERY_PARAMS.get('run', None)

        queryset = WorkflowRun.objects.all()
        if workflow:
            queryset = queryset.filter(workflow__uuid=workflow)
        if run:
            queryset = queryset.filter(run=run)

        return queryset


class WorkflowRunDetail(generics.RetrieveUpdateDestroyAPIView):
    model = WorkflowRun
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    serializer_class = WorkflowRunSerializer
