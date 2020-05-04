from rest_framework import (
    generics,
    permissions,
    filters
)

from rodan.models.resourcelabel import ResourceLabel
from rodan.permissions import CustomObjectPermissions
from rodan.serializers.resourcelabel import ResourceLabelSerializer
from rodan.paginators.pagination import CustomPaginationWithDisablePaginationOption


class ResourceLabelList(generics.ListAPIView):
    """
    """
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)
    queryset = ResourceLabel.objects.all()
    serializer_class = ResourceLabelSerializer
    pagination_class = CustomPaginationWithDisablePaginationOption
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = {
        "uuid": ["exact"],
        "name": ["exact", "icontains"],
    }


class ResourceLabelDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    """
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)
    queryset = ResourceLabel.objects.all()
    serializer_class = ResourceLabelSerializer
    filter_backends = ()
