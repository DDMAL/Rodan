from rest_framework import generics
from rest_framework import permissions
from rodan.models.outputporttype import OutputPortType
from rodan.serializers.outputporttype import OutputPortTypeSerializer


class OutputPortTypeList(generics.ListAPIView):
    """
    Returns a list of OutputPortTypes. Does not accept POST requests, since
    OutputPortTypes should be defined and loaded server-side.
    """
    model = OutputPortType
    serializer_class = OutputPortTypeSerializer
    permission_classes = (permissions.IsAuthenticated, )
    queryset = OutputPortType.objects.all()
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
    model = OutputPortType
    serializer_class = OutputPortTypeSerializer
    permission_classes = (permissions.IsAuthenticated, )
    queryset = OutputPortType.objects.all()
