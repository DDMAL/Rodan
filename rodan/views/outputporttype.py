from rest_framework import generics
from rest_framework import permissions, filters
from rodan.models.outputporttype import OutputPortType
from rodan.serializers.outputporttype import OutputPortTypeSerializer


class OutputPortTypeList(generics.ListAPIView):
    """
    Returns a list of OutputPortTypes. Does not accept POST requests, since
    OutputPortTypes should be defined and loaded server-side.
    """
    permission_classes = (permissions.AllowAny, )
    queryset = OutputPortType.objects.all()
    serializer_class = OutputPortTypeSerializer
    filter_backends = ()
    filter_fields = {
        "job": ['exact', 'icontains'],
        "minimum": ['exact', 'lt', 'gt'],
        "uuid": ['exact'],
        "name": ['exact', 'icontains'],
        "maximum": ['exact', 'lt', 'gt']
    }

class OutputPortTypeDetail(generics.RetrieveAPIView):
    """
    Query a single OutputPortType instance.
    """
    permission_classes = (permissions.AllowAny, )
    queryset = OutputPortType.objects.all()
    serializer_class = OutputPortTypeSerializer
    filter_backends = ()
