import django_filters
from rest_framework import generics
from rest_framework import permissions
from rodan.models.inputport import InputPort
from rodan.serializers.inputport import InputPortSerializer



class InputPortList(generics.ListCreateAPIView):
    """
    Returns a list of InputPorts. Accepts a POST request with a data body to create
    a new InputPort. POST requests will return the newly-created InputPort object.

    #### GET Parameters
    - `workflow_job`
    - `workflow`
    """
    model = InputPort
    serializer_class = InputPortSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = InputPort.objects.all() # [TODO] restrict to the user's objects?

    class filter_class(django_filters.FilterSet):
        workflow = django_filters.CharFilter(name='workflow_job__workflow')
        type = django_filters.CharFilter(name='input_port_type__name')
        class Meta:
            model = InputPort
            fields = ('type', 'workflow_job', 'workflow')


class InputPortDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Perform operations on a single InputPort instance.
    """
    model = InputPort
    serializer_class = InputPortSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = InputPort.objects.all() # [TODO] restrict to the user's objects?
