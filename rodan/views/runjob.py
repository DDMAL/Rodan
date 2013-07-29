from rest_framework import generics
from rest_framework import permissions

from rodan.models.runjob import RunJob
from rodan.models.runjob import RunJobStatus
from rodan.serializers.runjob import RunJobSerializer


class RunJobList(generics.ListAPIView):
    model = RunJob
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = RunJobSerializer
    paginate_by = None

    def get_queryset(self):
        requires_interaction = self.request.QUERY_PARAMS.get('requires_interaction', None)
        project = self.request.QUERY_PARAMS.get('project', None)
        workflowrun = self.request.QUERY_PARAMS.get('workflowrun', None)
        page = self.request.QUERY_PARAMS.get('page', None)
        queryset = RunJob.objects.all()
        if requires_interaction:
            queryset = queryset.filter(needs_input=1).filter(status__in=[RunJobStatus.WAITING_FOR_INPUT, RunJobStatus.RUN_ONCE_WAITING])
        if project:
            queryset = queryset.filter(workflow_job__workflow__project__uuid=project)
        if workflowrun:
            queryset = queryset.filter(workflow_run=workflowrun)
        if page:
            queryset = queryset.filter(page=page)

        return queryset


class RunJobDetail(generics.RetrieveUpdateAPIView):
    model = RunJob
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = RunJobSerializer
