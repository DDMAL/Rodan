from rest_framework import generics
from rest_framework import permissions
from rodan.models import ResourceType
from rodan.serializers.resourcetype import ResourceTypeSerializer
from rodan.paginators.pagination import PaginationSerializer


class ResourceTypeList(generics.ListAPIView):
    """
    Returns a list of all ResourceTypes. Does not accept POST requests, since
    ResourceTypes should be defined and loaded server-side.
    """
    model = ResourceType
    serializer_class = ResourceTypeSerializer
    pagination_serializer_class = PaginationSerializer
    permission_classes = (permissions.IsAuthenticated, )
    queryset = ResourceType.objects.all()
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
    model = ResourceType
    serializer_class = ResourceTypeSerializer
    permission_classes = (permissions.IsAuthenticated, )
    queryset = ResourceType.objects.all()
