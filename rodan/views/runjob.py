from rest_framework import generics
from rest_framework import permissions

from rodan.models.runjob import RunJob
from rodan.models.runjob import RunJobStatus
from rodan.serializers.runjob import RunJobSerializer


class RunJobList(generics.ListAPIView):
    """
    Returns a list of all RunJobs. Do not accept POST request as RunJobs are typically created by the server.

    #### Parameters
    - `requires_interaction` -- GET-only. If provided with any values, it will only
      return those RunJobs that currently require interaction.
    - `project` -- GET-only. UUID of a Project.
    - `workflowrun` -- GET-only. UUID of a WorkflowRun. [TODO] Rename to workflow_run??
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
            queryset = queryset.filter(needs_input=1).filter(status__in=[RunJobStatus.WAITING_FOR_INPUT, RunJobStatus.RUN_ONCE_WAITING]) # [TODO] ready_for_input?
        if project:
            queryset = queryset.filter(workflow_job__workflow__project__uuid=project)
        if workflowrun:
            queryset = queryset.filter(workflow_run=workflowrun)

        return queryset


class RunJobDetail(generics.RetrieveAPIView):
    """
    Performs operations on a single RunJob instance.
    """
    model = RunJob
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = RunJobSerializer
