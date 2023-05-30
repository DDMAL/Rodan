from rest_framework import (
    generics,
    permissions,
)
import django_filters.rest_framework as filters
from rest_framework.filters import OrderingFilter
from rodan.models.resourcelabel import ResourceLabel
from rodan.serializers.resourcelabel import ResourceLabelSerializer
from rodan.paginators.pagination import CustomPaginationWithDisablePaginationOption


class ResourceLabelList(generics.ListAPIView):
    """
    """
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ResourceLabel.objects.all()
    serializer_class = ResourceLabelSerializer
    pagination_class = CustomPaginationWithDisablePaginationOption
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter,)
    filter_fields = {
        "uuid": ["exact"],
        "name": ["exact", "icontains"],
    }    



class ResourceLabelDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    """
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ResourceLabel.objects.all()
    serializer_class = ResourceLabelSerializer
    filter_backends = ()
