from rest_framework import generics
from rest_framework import status
from rest_framework import permissions
from rest_framework.response import Response
from rodan.models.resourcecollection import ResourceCollection
from rodan.models.inputport import InputPort
from rodan.serializers.resourcecollection import ResourceCollectionSerializer


class ResourceCollectionList(generics.ListCreateAPIView):
    """
    Returns a list of ResourceCollections. Accepts a POST request with a data body
    to create a new ResourceCollection. POST requests will return the newly-created
    ResourceCollection object.

    #### Parameters
    - workflow -- POST-only, URL to an Workflow object
    - resources -- POST-only, a list of URL to Resource objects.
    """
    model = ResourceCollection
    serializer_class = ResourceCollectionSerializer
    permission_classes = (permissions.IsAuthenticated, )
    queryset = ResourceCollection.objects.all() # [TODO] filter according to the user?

class ResourceCollectionDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Perform operations on a single ResourceCollection instance.
    """
    model = ResourceCollection
    serializer_class = ResourceCollectionSerializer
    permission_classes = (permissions.IsAuthenticated, )
    queryset = ResourceCollection.objects.all() # [TODO] filter according to the user?
