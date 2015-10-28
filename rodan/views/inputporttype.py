from rest_framework import status
from rest_framework import generics
from rest_framework import permissions, filters
from rodan.models.inputporttype import InputPortType
from rodan.serializers.inputporttype import InputPortTypeSerializer


class InputPortTypeList(generics.ListAPIView):
    """
    Returns a list of InputPortTypes. Does not accept POST requests, since
    InputPortTypes should be defined and loaded server-side.
    """
    permission_classes = (permissions.AllowAny, )
    queryset = InputPortType.objects.all()
    serializer_class = InputPortTypeSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
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
    permission_classes = (permissions.AllowAny, )
    queryset = InputPortType.objects.all()
    serializer_class = InputPortTypeSerializer
    filter_backends = ()
