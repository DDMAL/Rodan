from rest_framework import generics
from rest_framework import status
from rest_framework import permissions
from rest_framework.response import Response
from django.core.urlresolvers import Resolver404
from rodan.helpers.object_resolving import resolve_to_object
from rodan.models.resourceassignment import ResourceAssignment
from rodan.models.inputport import InputPort
from rodan.serializers.resourceassignment import ResourceAssignmentSerializer


class ResourceAssignmentList(generics.ListCreateAPIView):
    """
    Returns a list of ResourceAssignments. Accepts a POST request with a data body
    to create a new ResourceAssignments. POST requests will return the newly-created
    ResourceAssignment object.

    #### Parameters
    - input_port -- POST-only, URL to an InputPort object
    - resources -- POST-only, a list of URL to Resource objects.
    """
    model = ResourceAssignment
    serializer_class = ResourceAssignmentSerializer
    permission_classes = (permissions.IsAuthenticated, )
    queryset = ResourceAssignment.objects.all() # [TODO] filter according to the user?

class ResourceAssignmentDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Perform operations on a single ResourceAssignment instance.
    """
    model = ResourceAssignment
    serializer_class = ResourceAssignmentSerializer
    permission_classes = (permissions.IsAuthenticated, )
    queryset = ResourceAssignment.objects.all() # [TODO] filter according to the user?
