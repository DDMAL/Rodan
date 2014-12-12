from rest_framework import generics
from rest_framework import permissions
from rodan.models import ResourceType
from rodan.serializers.resourcetype import ResourceTypeSerializer


class ResourceTypeList(generics.ListAPIView):
    """
    Returns a list of all ResourceTypes. Does not accept POST requests, since
    ResourceTypes should be defined and loaded server-side.
    """
    model = ResourceType
    serializer_class = ResourceTypeSerializer
    permission_classes = (permissions.IsAuthenticated, )
    queryset = ResourceType.objects.all()


class ResourceTypeDetail(generics.RetrieveAPIView):
    """
    Query a single ResourceType instance.
    """
    model = ResourceType
    serializer_class = ResourceTypeSerializer
    permission_classes = (permissions.IsAuthenticated, )
    queryset = ResourceType.objects.all()
