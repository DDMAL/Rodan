import django_filters
from rest_framework import generics
from rest_framework import permissions
from rodan.models.outputport import OutputPort
from rodan.serializers.outputport import OutputPortSerializer
from rodan.permissions import CustomObjectPermissions
from rest_framework import filters


class OutputPortList(generics.ListCreateAPIView):
    """
    Returns a list of OutputPorts. Accepts a POST request with a data body to create
    a new OutputPort. POST requests will return the newly-created OutputPort object.
    """
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions, )
    _ignore_model_permissions = True
    queryset = OutputPort.objects.all()
    serializer_class = OutputPortSerializer

    class filter_class(django_filters.FilterSet):
        workflow = django_filters.CharFilter(name='workflow_job__workflow')
        type = django_filters.CharFilter(name='output_port_type__name')
        class Meta:
            model = OutputPort
            fields = (
                "extern",
                "output_port_type",
                "workflow_job",
                "uuid",
                "label"
            )


class OutputPortDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Perform operations on a single OutputPort instance.
    """
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions, )
    _ignore_model_permissions = True
    queryset = OutputPort.objects.all()
    serializer_class = OutputPortSerializer
