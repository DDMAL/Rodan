import django_filters
from rest_framework import generics
from rest_framework import permissions
from rodan.models.outputport import OutputPort
from rodan.serializers.outputport import OutputPortSerializer
from rodan.permissions import CustomObjectPermissions
from rodan.exceptions import CustomAPIException
from rest_framework import status


class OutputPortList(generics.ListCreateAPIView):
    """
    Returns a list of OutputPorts. Accepts a POST request with a data body to create
    a new OutputPort. POST requests will return the newly-created OutputPort object.
    """

    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)
    _ignore_model_permissions = True
    queryset = OutputPort.objects.all()
    serializer_class = OutputPortSerializer

    class filter_class(django_filters.FilterSet):
        workflow = django_filters.CharFilter(name="workflow_job__workflow")
        type = django_filters.CharFilter(name="output_port_type__name")

        class Meta:
            model = OutputPort
            fields = ("extern", "output_port_type", "workflow_job", "uuid", "label")


class OutputPortDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Perform operations on a single OutputPort instance.
    """

    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)
    _ignore_model_permissions = True
    queryset = OutputPort.objects.all()
    serializer_class = OutputPortSerializer

    def perform_update(self, op_serializer):
        if op_serializer.instance.workflow_job.group is not None:
            invalid_info = {}
            for k, v in op_serializer.validated_data.iteritems():
                invalid_info[
                    k
                ] = "To modify this field, you should first remove its workflow job from the group."
            if invalid_info:
                raise CustomAPIException(
                    invalid_info, status=status.HTTP_400_BAD_REQUEST
                )
        op_serializer.save()

    def perform_destroy(self, op):
        if op.workflow_job.group is not None:
            raise CustomAPIException(
                "To delete this output port, you should first remove its workflow job from the group.",
                status=status.HTTP_400_BAD_REQUEST,
            )
        op.delete()
