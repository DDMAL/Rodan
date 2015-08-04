from rest_framework import generics
from rest_framework import permissions
import django_filters
from rodan.models import WorkflowJobCoordinateSet
from rodan.paginators.pagination import PaginationSerializer
from rodan.serializers.workflowjobcoordinateset import WorkflowJobCoordinateSetSerializer


class WorkflowJobCoordinateSetList(generics.ListCreateAPIView):
    """
    Returns a list of all WorkflowJobCoordinateSets. Accepts a POST request
    with a data body to create a new WorkflowJobCoordinateSet. POST requests
    will return the newly-created WorkflowJobCoordinateSet object.

    #### GET Parameters
    - `workflow`
    - `workflow_job`
    """
    model = WorkflowJobCoordinateSet
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = WorkflowJobCoordinateSetSerializer
    pagination_serializer_class = PaginationSerializer
    queryset = WorkflowJobCoordinateSet.objects.all() # [TODO] filter according to the user?

    class filter_class(django_filters.FilterSet):
        workflow = django_filters.CharFilter(name="workflow_job__workflow")
        class Meta:
            model = WorkflowJobCoordinateSet
            fields = ('workflow', 'workflow_job')


class WorkflowJobCoordinateSetDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Performs operations on a single WorkflowJobCoordinateSet instance.
    """
    model = WorkflowJobCoordinateSet
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = WorkflowJobCoordinateSetSerializer
    queryset = WorkflowJobCoordinateSet.objects.all() # [TODO] filter according to the user?
