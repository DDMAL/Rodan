from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rodan.models.inputporttype import InputPortType
from rodan.serializers.inputporttype import InputPortTypeSerializer


class InputPortTypeList(generics.ListAPIView):
    """
    Returns a list of InputPortTypes. Does not accept POST requests, since
    InputPortTypes should be defined and loaded server-side.

    #### Parameters
    - `job` -- GET. UUID of a Job.
    """
    model = InputPortType
    serializer_class = InputPortTypeSerializer
    permission_classes = (permissions.IsAuthenticated, )
    queryset = InputPortType.objects.all()
    filter_fields = ('job', )


class InputPortTypeDetail(generics.RetrieveAPIView):
    """
    Query a single InputPortType instance.
    """
    model = InputPortType
    serializer_class = InputPortTypeSerializer
    permission_classes = (permissions.IsAuthenticated, )
    queryset = InputPortType.objects.all()
