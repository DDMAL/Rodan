import django_filters
from rest_framework import generics
from rest_framework import permissions
from rodan.models.inputport import InputPort
from rodan.serializers.inputport import InputPortSerializer
from rodan.paginators.pagination import PaginationSerializer
from django.db.models import Q


class InputPortList(generics.ListCreateAPIView):
    """
    Returns a list of InputPorts. Accepts a POST request with a data body to create
    a new InputPort. POST requests will return the newly-created InputPort object.

    #### Other GET Parameters
    - `has_connections` -- if `true/True/TRUE`, return "satisfied" InputPorts only;
      if `false/False/FALSE`, return "unsatisfied" InputPorts only; other values
      will be ignored.
    """
    model = InputPort
    serializer_class = InputPortSerializer
    pagination_serializer_class = PaginationSerializer
    permission_classes = (permissions.IsAuthenticated,)

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
    model = InputPort
    serializer_class = InputPortSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = InputPort.objects.all() # [TODO] restrict to the user's objects?
