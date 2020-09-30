from rest_framework import generics
from rest_framework import permissions

import django_filters

from rodan.models.runjob import RunJob
from rodan.serializers.runjob import RunJobSerializer
from rodan.permissions import CustomObjectPermissions


class RunJobList(generics.ListAPIView):
    """
    Returns a list of all RunJobs. Do not accept POST request as RunJobs are typically created by
    the server.
    """

    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)
    _ignore_model_permissions = True
    queryset = RunJob.objects.all()
    serializer_class = RunJobSerializer

    class filter_class(django_filters.FilterSet):
        project = django_filters.CharFilter(name="workflow_run__project")
        resource_uuid__isnull = django_filters.BooleanFilter(
            # action=lambda q, v: q.filter(resource_uuid__isnull=v)
            method=lambda q, v: q.filter(resource_uuid__isnull=v)
        )  # https://github.com/alex/django-filter/issues/273

        class Meta:
            model = RunJob
            fields = {
                "status": ["exact"],
                "updated": ["lt", "gt"],
                "uuid": ["exact"],
                "created": ["lt", "gt"],
                "workflow_run": ["exact"],
                "workflow_job_uuid": ["exact"],
                "resource_uuid": ["exact"],
                "job_name": ["exact", "icontains"],
            }


class RunJobDetail(generics.RetrieveAPIView):
    """
    Performs operations on a single RunJob instance.
    """

    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)
    _ignore_model_permissions = True
    queryset = RunJob.objects.all()
    serializer_class = RunJobSerializer
