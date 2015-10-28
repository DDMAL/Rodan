from rest_framework import generics, filters
from rest_framework import permissions
from rodan.models import ResourceType
from rodan.serializers.resourcetype import ResourceTypeSerializer


class ResourceTypeList(generics.ListAPIView):
    """
    Returns a list of all ResourceTypes. Does not accept POST requests, since
    ResourceTypes should be defined and loaded server-side.
    """
    permission_classes = (permissions.AllowAny, )
    queryset = ResourceType.objects.all()
    serializer_class = ResourceTypeSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = {
        "mimetype": ['exact', 'icontains'],
        "uuid": ['exact'],
        "extension": ['exact'],
        "description": ['icontains']
    }


class ResourceTypeDetail(generics.RetrieveAPIView):
    """
    Query a single ResourceType instance.
    """
    permission_classes = (permissions.AllowAny, )
    queryset = ResourceType.objects.all()
    serializer_class = ResourceTypeSerializer
    filter_backends = ()
