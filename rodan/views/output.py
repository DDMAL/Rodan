from rest_framework import generics
from rest_framework import permissions
from rodan.models.output import Output
from rodan.serializers.output import OutputSerializer, OutputListSerializer


class OutputList(generics.ListAPIView):
    """
    Returns a list of Outputs. Do not accept POST request as Outputs are typically created by the server.

    #### Parameters
    - `run_job` -- GET-only. UUID of a RunJob object.
    """
    model = Output
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = OutputListSerializer
    filter_fields = ('run_job', )


class OutputDetail(generics.RetrieveAPIView):
    """
    Query a single Output instance.
    """
    model = Output
    serializer_class = OutputSerializer
    permission_classes = (permissions.IsAuthenticated, )
