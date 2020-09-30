from rest_framework import generics, filters
from rest_framework import permissions, status
from rodan.models import ResourceList
from rodan.serializers.resourcelist import ResourceListSerializer
from rodan.permissions import CustomObjectPermissions
import django_filters
from rest_framework.response import Response


class ResourceListList(generics.ListCreateAPIView):
    """
    Returns a list of all ResourceLists.
    """

    queryset = ResourceList.objects.all()
    serializer_class = ResourceListSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)

    class filter_class(django_filters.FilterSet):
        origin__isnull = django_filters.BooleanFilter(
            # django-filter 0.9.x
            # action=lambda q, v: q.filter(origin__isnull=v)
            method=lambda q, v: q.filter(origin__isnull=v)
        )  # https://github.com/alex/django-filter/issues/273

        # django-filter 0.9.x
        # resource_type__in = django_filters.MethodFilter()
        # def filter_resource_type__in(self, q, v):
        #     vs = v.split(",")
        #     return q.filter(resource_type__uuid__in=vs)
        resource_type__in = django_filters.filters.CharFilter(method="filter_resource_type__in")

        def filter_resource_type__in(self, qs, name, value):
            value = value.split(",")
            return qs.filter(**{name: value})

        class Meta:
            model = ResourceList
            fields = {
                "uuid": ["exact"],
                "name": ["exact", "icontains"],
                "description": ["icontains"],
                "project": ["exact"],
                "origin": ["exact"],
                "created": ["gt", "lt"],
                "updated": ["gt", "lt"],
            }

    def post(self, request, *args, **kwargs):
        serializer = ResourceListSerializer(
            context={"request": request}, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        resourcelist_obj = serializer.save(creator=request.user)
        d = ResourceListSerializer(resourcelist_obj, context={"request": request}).data
        return Response(d, status=status.HTTP_201_CREATED)


class ResourceListDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Query a single ResourceList instance.
    """

    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)
    queryset = ResourceList.objects.all()
    serializer_class = ResourceListSerializer
    filter_backends = ()

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
