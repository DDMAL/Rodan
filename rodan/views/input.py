from rest_framework import generics
from rest_framework import permissions
from rodan.models.input import Input
from rodan.serializers.input import InputSerializer


class InputList(generics.ListAPIView):
    """
    Returns a list of Inputs. Do not accept POST request as Inputs are typically created by the server.
    """
    model = Input
    serializer_class = InputSerializer
    permission_classes = (permissions.IsAuthenticated, )
    queryset = Input.objects.all() # [TODO] restrict to the user's inputs?
    filter_fields = (
        "resource",
        "run_job",
        "uuid",
        "input_port_type_name"
    )


class InputDetail(generics.RetrieveAPIView):
    """
    Query a single Input instance.
    """
    model = Input
    serializer_class = InputSerializer
    permission_classes = (permissions.IsAuthenticated, )
    queryset = Input.objects.all() # [TODO] restrict to the user's inputs?
