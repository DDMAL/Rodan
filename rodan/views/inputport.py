import django_filters
from rest_framework import generics
from rest_framework import permissions
from rodan.models.inputport import InputPort
from rodan.serializers.inputport import InputPortSerializer
from django.db.models import Q
from rodan.permissions import CustomObjectPermissions
from rest_framework import filters
from rodan.exceptions import CustomAPIException
from rest_framework import status


class InputPortList(generics.ListCreateAPIView):
    """
    Returns a list of InputPorts. Accepts a POST request with a data body to create
    a new InputPort. POST requests will return the newly-created InputPort object.

    #### Other GET Parameters
    - `has_connections` -- if `true/True/TRUE`, return "satisfied" InputPorts only;
      if `false/False/FALSE`, return "unsatisfied" InputPorts only; other values
      will be ignored.
    """
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions, )
    _ignore_model_permissions = True
    queryset = InputPort.objects.all()
    serializer_class = InputPortSerializer

    class filter_class(django_filters.FilterSet):
        workflow = django_filters.CharFilter(name='workflow_job__workflow')
        type = django_filters.CharFilter(name='input_port_type__name')
        class Meta:
            model = InputPort
            fields = (
                "extern",
                "input_port_type",
                "workflow_job",
                "uuid",
                "label"
            )

    def get_queryset(self):
        condition = Q()  # ground value

        has_connections = self.request.query_params.get('has_connections', None)
        if has_connections and has_connections.lower() == 'false':
            condition &= Q(connections__isnull=True)
        elif has_connections and has_connections.lower() == 'true':
            condition &= Q(connections__isnull=False)

        queryset = InputPort.objects.filter(condition)
        return queryset


class InputPortDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Perform operations on a single InputPort instance.
    """
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions, )
    _ignore_model_permissions = True
    queryset = InputPort.objects.all()
    serializer_class = InputPortSerializer

    def perform_update(self, ip_serializer):
        if ip_serializer.instance.workflow_job.group is not None:
            invalid_info = {}
            for k, v in ip_serializer.validated_data.iteritems():
                invalid_info[k] = "To modify this field, you should first remove its workflow job from the group."
            if invalid_info:
                raise CustomAPIException(invalid_info, status=status.HTTP_400_BAD_REQUEST)
        ip_serializer.save()

    def perform_destroy(self, ip):
        if ip.workflow_job.group is not None:
            raise CustomAPIException("To delete this input port, you should first remove its workflow job from the group.", status=status.HTTP_400_BAD_REQUEST)
        ip.delete()
