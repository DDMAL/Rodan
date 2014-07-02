from rest_framework import generics
from rodan.models.connection import Connection
from rodan.serializers.connection import ConnectionSerializer


class ConnectionList(generics.ListCreateAPIView):
    model = Connection
    serializer_class = ConnectionSerializer


class ConnectionDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Connection
    serializer_class = ConnectionSerializer
