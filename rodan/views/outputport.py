from rest_framework import generics
from rest_framework import permissions
from rodan.models.outputport import OutputPort
from rodan.serializers.outputport import OutputPortSerializer


class OutputPortList(generics.ListCreateAPIView):
    """
    Returns a list of OutputPorts. Accepts a POST request with a data body to create
    a new OutputPort. POST requests will return the newly-created OutputPort object.
    """
    model = OutputPort
    serializer_class = OutputPortSerializer
    permission_classes = (permissions.IsAuthenticated,)


class OutputPortDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Perform operations on a single OutputPort instance.
    """
    model = OutputPort
    serializer_class = OutputPortSerializer
    permission_classes = (permissions.IsAuthenticated,)
