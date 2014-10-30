from rest_framework import generics
from rest_framework import permissions
from rodan.models.input import Input
from rodan.serializers.input import InputSerializer


class InputList(generics.ListAPIView):
    """
    Returns a list of Inputs. Do not accept POST request as Inputs are typically created by the server.

    #### Parameters
    - `run_job` -- GET-only. UUID of a RunJob object.
    """
    model = Input
    paginate_by = None
    permission_classes = (permissions.IsAuthenticated, )
    filter_fields = ('run_job', )


class InputDetail(generics.RetrieveAPIView):
    """
    Query a single Input instance.
    """
    model = Input
    serializer_class = InputSerializer
    permission_classes = (permissions.IsAuthenticated, )
