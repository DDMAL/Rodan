from rest_framework import generics, filters
from rest_framework import permissions
from rodan.models import ResourceList
from rodan.serializers.resourcelist import ResourceListSerializer
import django_filters

class ResourceListList(generics.ListCreateAPIView):
    """
    Returns a list of all ResourceLists. Does not accept POST requests, since
    ResourceLists should be defined and loaded server-side.
    """
    queryset = ResourceList.objects.all()
    serializer_class = ResourceListSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)

    class filter_class(django_filters.FilterSet):
        origin__isnull = django_filters.BooleanFilter(action=lambda q, v: q.filter(origin__isnull=v))  # https://github.com/alex/django-filter/issues/273
        resource_type__in = django_filters.MethodFilter()

        def filter_resource_type__in(self, q, v):
            vs = v.split(',')
            return q.filter(resource_type__uuid__in=vs)

        class Meta:
            model = ResourceList
            fields = {
                "uuid": ['exact'],
                "name": ['exact', 'icontains'],
                "description": ['icontains'],
                "project": ['exact'],
                "resource_type": ['exact'],
                "origin": ['exact'],
                "created": ['gt', 'lt'],
                "updated": ['gt', 'lt'],
            }


class ResourceListDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Query a single ResourceList instance.
    """
    queryset = ResourceList.objects.all()
    serializer_class = ResourceListSerializer
    filter_backends = ()
