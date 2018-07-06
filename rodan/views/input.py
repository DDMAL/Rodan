from rest_framework import generics
from rest_framework import permissions
from rodan.models.input import Input
from rodan.serializers.input import InputSerializer
from rodan.permissions import CustomObjectPermissions


class InputList(generics.ListAPIView):
    """
    Returns a list of Inputs. Do not accept POST request as Inputs are typically created by the server.
    """

    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)
    _ignore_model_permissions = True
    queryset = Input.objects.all()
    serializer_class = InputSerializer
    filter_fields = ("resource", "run_job", "uuid", "input_port_type_name")


class InputDetail(generics.RetrieveAPIView):
    """
    Query a single Input instance.
    """

    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)
    _ignore_model_permissions = True
    queryset = Input.objects.all()
    serializer_class = InputSerializer
