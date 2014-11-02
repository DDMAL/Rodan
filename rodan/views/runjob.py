from rest_framework import generics
from rest_framework import permissions
import django_filters
from rodan.models.runjob import RunJob
from rodan.models.runjob import RunJobStatus
from rodan.serializers.runjob import RunJobSerializer

class RunJobFilter(django_filters.FilterSet):
    project = django_filters.CharFilter(name="workflow_run__workflow__project")
    class Meta:
        model = RunJob
        fields = ('ready_for_input', 'project', 'workflow_run')

class RunJobList(generics.ListAPIView):
    """
    Returns a list of all RunJobs. Do not accept POST request as RunJobs are typically created by the server.

    #### Parameters
    - `ready_for_input` -- GET-only. Boolean value: True/False.
    - `project` -- GET-only. UUID of a Project.
    - `workflow_run` -- GET-only. UUID of a WorkflowRun.
    """
    model = RunJob
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = RunJobSerializer
    filter_class = RunJobFilter


class RunJobDetail(generics.RetrieveAPIView):
    """
    Performs operations on a single RunJob instance.
    """
    model = RunJob
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = RunJobSerializer
