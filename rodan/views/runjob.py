from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from celery import registry
from celery.task.control import revoke

from django.db.models import Q
from django.conf import settings
import django_filters

from rodan.models.runjob import RunJob
from rodan.serializers.runjob import RunJobSerializer
from rodan.constants import task_status
from rodan.exceptions import CustomAPIException
from rodan.paginators.pagination import PaginationSerializer

class RunJobList(generics.ListAPIView):
    """
    Returns a list of all RunJobs. Do not accept POST request as RunJobs are typically created by the server.
    """
    model = RunJob
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = RunJobSerializer
    pagination_serializer_class = PaginationSerializer
    queryset = RunJob.objects.all() # [TODO] filter according to the user?

    class filter_class(django_filters.FilterSet):
        project = django_filters.CharFilter(name="workflow_run__project")
        resource_uuid__isnull = django_filters.BooleanFilter(action=lambda q, v: q.filter(resource_uuid__isnull=v))  # https://github.com/alex/django-filter/issues/273
        class Meta:
            model = RunJob
            fields = {
                "status": ['exact'],
                "updated": ['lt', 'gt'],
                "uuid": ['exact'],
                "created": ['lt', 'gt'],
                "workflow_run": ['exact'],
                "workflow_job_uuid": ['exact'],
                "resource_uuid": ['exact'],
                "job_name": ['exact', 'icontains'],
            }


class RunJobDetail(generics.RetrieveAPIView):
    """
    Performs operations on a single RunJob instance.
    """
    model = RunJob
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = RunJobSerializer
    queryset = RunJob.objects.all() # [TODO] filter according to the user?
