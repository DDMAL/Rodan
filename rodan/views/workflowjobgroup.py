from rest_framework import generics
from rest_framework import permissions
import django_filters
from rodan.paginators.pagination import PaginationSerializer
from rodan.models import WorkflowJobGroup
from rodan.serializers.workflowjobgroup import WorkflowJobGroupSerializer


class WorkflowJobGroupList(generics.ListCreateAPIView):
    """
    Returns a list of all WorkflowJobGroups. Accepts a POST request with a data body
    to create a new WorkflowJobGroup. POST requests will return the newly-created
    WorkflowJobGroup object.

    #### Other POST Parameters
    - `workflow_jobs`
    """
    model = WorkflowJobGroup
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = WorkflowJobGroupSerializer
    pagination_serializer_class = PaginationSerializer
    filter_fields = ('origin', )
    queryset = WorkflowJobGroup.objects.all() # [TODO] filter according to the user?

    class filter_class(django_filters.FilterSet):
        workflow = django_filters.CharFilter(name="workflow_jobs__workflow")
        project = django_filters.CharFilter(name="workflow_jobs__workflow__project")
        class Meta:
            model = WorkflowJobGroup
            fields = {
                "origin": ['exact'],
                "updated": ['lt', 'gt'],
                "uuid": ['exact'],
                "name": ['exact'],
                "created": ['lt', 'gt']
            }

class WorkflowJobGroupDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Performs operations on a single WorkflowJobGroup instance.
    """
    model = WorkflowJobGroup
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = WorkflowJobGroupSerializer
    queryset = WorkflowJobGroup.objects.all() # [TODO] filter according to the user?
