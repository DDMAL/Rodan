from rest_framework import generics
from rest_framework import permissions
import django_filters
from rodan.models.runjob import RunJob
from rodan.serializers.runjob import RunJobSerializer

class RunJobList(generics.ListAPIView):
    """
    Returns a list of all RunJobs. Do not accept POST request as RunJobs are typically created by the server.

    #### Parameters
    - `status` -- GET-only. Status number.
    - `project` -- GET-only. UUID of a Project.
    - `workflow_run` -- GET-only. UUID of a WorkflowRun.
    """
    model = RunJob
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = RunJobSerializer
    queryset = RunJob.objects.all() # [TODO] filter according to the user?

    class filter_class(django_filters.FilterSet):
        project = django_filters.CharFilter(name="workflow_run__workflow__project")
        class Meta:
            model = RunJob
            fields = ('status', 'project', 'workflow_run')


class RunJobDetail(generics.RetrieveAPIView):
    """
    Performs operations on a single RunJob instance.
    """
    model = RunJob
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = RunJobSerializer
    queryset = RunJob.objects.all() # [TODO] filter according to the user?
