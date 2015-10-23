from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rodan.models.inputporttype import InputPortType
from rodan.serializers.inputporttype import InputPortTypeSerializer
from rodan.paginators.pagination import PaginationSerializer


class InputPortTypeList(generics.ListAPIView):
    """
    Returns a list of InputPortTypes. Does not accept POST requests, since
    InputPortTypes should be defined and loaded server-side.
    """
    model = InputPortType
    serializer_class = InputPortTypeSerializer
    pagination_serializer_class = PaginationSerializer
    permission_classes = (permissions.IsAuthenticated, )
    queryset = InputPortType.objects.all()
    filter_fields = {
        "job": ['exact', 'icontains'],
        "minimum": ['exact', 'lt', 'gt'],
        "uuid": ['exact'],
        "name": ['exact', 'icontains'],
        "maximum": ['exact', 'lt', 'gt']
    }


class InputPortTypeDetail(generics.RetrieveAPIView):
    """
    Query a single InputPortType instance.
    """
    model = InputPortType
    serializer_class = InputPortTypeSerializer
    permission_classes = (permissions.IsAuthenticated, )
    queryset = InputPortType.objects.all()
