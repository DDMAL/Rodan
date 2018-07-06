from rest_framework import generics
from rest_framework import permissions
from rodan.models.output import Output
from rodan.serializers.output import OutputSerializer, OutputListSerializer


class OutputList(generics.ListAPIView):
    """
    Returns a list of Outputs. Do not accept POST request as Outputs are typically created by the server.
    """

    model = Output
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = OutputListSerializer
    filter_fields = ("resource", "run_job", "uuid", "output_port_type_name")
    queryset = Output.objects.all()  # [TODO] restrict to the user's outputs?


class OutputDetail(generics.RetrieveAPIView):
    """
    Query a single Output instance.
    """

    model = Output
    serializer_class = OutputSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Output.objects.all()  # [TODO] restrict to the user's outputs?
