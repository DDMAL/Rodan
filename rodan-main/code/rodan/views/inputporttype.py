from rest_framework import generics
from rest_framework import permissions
import django_filters.rest_framework as filters
from rest_framework.filters import OrderingFilter

from rodan.models.inputporttype import InputPortType
from rodan.serializers.inputporttype import InputPortTypeSerializer
from rodan.paginators.pagination import CustomPaginationWithDisablePaginationOption


class InputPortTypeList(generics.ListAPIView):
    """
    Returns a list of InputPortTypes. Does not accept POST requests, since
    InputPortTypes should be defined and loaded server-side.
    """

    permission_classes = (permissions.AllowAny,)
    queryset = InputPortType.objects.all()
    serializer_class = InputPortTypeSerializer
    pagination_class = CustomPaginationWithDisablePaginationOption
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter,)
    filter_fields = {
        # "job": ["exact", "icontains"],
        "job": ["exact", ],
        "minimum": ["exact", "lt", "gt"],
        "uuid": ["exact"],
        "name": ["exact", "icontains"],
        "maximum": ["exact", "lt", "gt"],
    }


class InputPortTypeDetail(generics.RetrieveAPIView):
    """
    Query a single InputPortType instance.
    """

    permission_classes = (permissions.AllowAny,)
    queryset = InputPortType.objects.all()
    serializer_class = InputPortTypeSerializer
    filter_backends = ()
