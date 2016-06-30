import django_filters
from rest_framework import generics
from rest_framework import permissions
from rodan.models.connection import Connection
from rodan.serializers.connection import ConnectionSerializer
from rodan.permissions import CustomObjectPermissions
from rodan.exceptions import CustomAPIException
from rest_framework import status


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

    def perform_update(self, conn_serializer):
        if conn_serializer.instance.input_port.workflow_job.group is not None and conn_serializer.instance.input_port.workflow_job.group == conn_serializer.instance.output_port.workflow_job.group:
            invalid_info = {}
            for k, v in conn_serializer.validated_data.iteritems():
                invalid_info[k] = "To modify this field, you should first remove one of its related workflow jobs from the group."
            if invalid_info:
                raise CustomAPIException(invalid_info, status=status.HTTP_400_BAD_REQUEST)
        conn_serializer.save()

    def perform_destroy(self, conn):
        if conn.input_port.workflow_job.group is not None and conn.input_port.workflow_job.group == conn.output_port.workflow_job.group:
            raise CustomAPIException("To delete this connection, you should first remove one of its related workflow jobs from the group.", status=status.HTTP_400_BAD_REQUEST)
        conn.delete()
