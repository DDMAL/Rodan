import django_filters
from rest_framework import generics
from rest_framework import status
from rest_framework import permissions
from rest_framework.response import Response
from rodan.models.connection import Connection
from rodan.models.inputport import InputPort
from rodan.models.outputport import OutputPort
from rodan.serializers.connection import ConnectionSerializer
from rodan.permissions import CustomObjectPermissions
from rest_framework import filters


class ConnectionList(generics.ListCreateAPIView):
    """
    Returns a list of Connections. Accepts a POST request with a data body to create
    a new Connection. POST requests will return the newly-created Connection object.
    """
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions, )
    _ignore_model_permissions = True
    queryset = Connection.objects.all()
    serializer_class = ConnectionSerializer

    class filter_class(django_filters.FilterSet):
        workflow = django_filters.CharFilter(name="output_port__workflow_job__workflow")
        input_workflow_job = django_filters.CharFilter(name="input_port__workflow_job")
        output_workflow_job = django_filters.CharFilter(name="output_port__workflow_job")
        class Meta:
            model = Connection
            fields = {
                "output_port": ['exact'],
                "input_port": ['exact'],
                "uuid": ['exact']
            }


class ConnectionDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Perform operations on a single Connection instance.
    """
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions, )
    _ignore_model_permissions = True
    queryset = Connection.objects.all()
    serializer_class = ConnectionSerializer
