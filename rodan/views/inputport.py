from rest_framework import generics
from rest_framework import permissions
from rodan.models.inputport import InputPort
from rodan.serializers.inputport import InputPortSerializer


class InputPortList(generics.ListCreateAPIView):
    """
    Returns a list of InputPorts. Accepts a POST request with a data body to create
    a new InputPort. POST requests will return the newly-created InputPort object.
    """
    model = InputPort
    serializer_class = InputPortSerializer
    permission_classes = (permissions.IsAuthenticated, )
    paginate_by = None


class InputPortDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Perform operations on a single InputPort instance.
    """
    model = InputPort
    serializer_class = InputPortSerializer
    permission_classes = (permissions.IsAuthenticated, )
