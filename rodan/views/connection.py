from rest_framework import generics
from rest_framework import status
from rest_framework import permissions
from rest_framework.response import Response
from rodan.models.connection import Connection
from rodan.models.inputport import InputPort
from rodan.models.outputport import OutputPort
from rodan.serializers.connection import ConnectionListSerializer, ConnectionSerializer


class ConnectionList(generics.ListCreateAPIView):
    """
    Returns a list of Connections. Accepts a POST request with a data body to create
    a new Connection. POST requests will return the newly-created Connection object.

    #### Parameters
    - input_port -- POST-only, URL to an InputPort object
    - output_port -- POST-only, URL to an OutputPort object
    """
    model = Connection
    serializer_class = ConnectionListSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Connection.objects.all()  # [TODO] restrict to the users connections?


class ConnectionDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Perform operations on a single Connection instance.
    """
    model = Connection
    serializer_class = ConnectionSerializer
    permission_classes = (permissions.IsAuthenticated, )
    queryset = Connection.objects.all()  # [TODO] restrict to the users connections?
