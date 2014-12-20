import django_filters
from rest_framework import generics
from rest_framework import status
from rest_framework import permissions
from rest_framework.response import Response
from rodan.models.resourceassignment import ResourceAssignment
from rodan.models.inputport import InputPort
from rodan.serializers.resourceassignment import ResourceAssignmentSerializer


class ResourceAssignmentList(generics.ListCreateAPIView):
    """
    Returns a list of ResourceAssignments. Accepts a POST request with a data body
    to create a new ResourceAssignments. POST requests will return the newly-created
    ResourceAssignment object.

    #### GET Parameters
    - `workflow`
    - `workflow_job`
    - `input_port`

    #### POST Parameters
    - `input_port`
    - `resource`
    - `resource_collection`
    """
    model = ResourceAssignment
    serializer_class = ResourceAssignmentSerializer
    permission_classes = (permissions.IsAuthenticated, )
    queryset = ResourceAssignment.objects.all() # [TODO] filter according to the user?

    class filter_class(django_filters.FilterSet):
        workflow = django_filters.CharFilter(name='input_port__workflow_job__workflow')
        workflow_job = django_filters.CharFilter(name='input_port__workflow_job')
        class Meta:
            model = ResourceAssignment
            fields = ('workflow_job', 'workflow', 'input_port')

class ResourceAssignmentDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Perform operations on a single ResourceAssignment instance.
    """
    model = ResourceAssignment
    serializer_class = ResourceAssignmentSerializer
    permission_classes = (permissions.IsAuthenticated, )
    queryset = ResourceAssignment.objects.all() # [TODO] filter according to the user?
