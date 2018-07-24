from rest_framework import generics
from rest_framework import permissions
import django_filters
from rodan.models import WorkflowJobGroupCoordinateSet
from rodan.serializers.workflowjobgroupcoordinateset import (
    WorkflowJobGroupCoordinateSetSerializer
)
from rodan.permissions import CustomObjectPermissions


class WorkflowJobGroupCoordinateSetList(generics.ListCreateAPIView):
    """
    Returns a list of all WorkflowJobGroupCoordinateSets. Accepts a POST request
    with a data body to create a new WorkflowJobCoordinateSet. POST requests
    will return the newly-created WorkflowJobCoordinateSet object.
    """

    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)
    _ignore_model_permissions = True
    queryset = WorkflowJobGroupCoordinateSet.objects.all()
    serializer_class = WorkflowJobGroupCoordinateSetSerializer

    class filter_class(django_filters.FilterSet):
        workflow = django_filters.CharFilter(name="workflow_job_group__workflow")

        class Meta:
            model = WorkflowJobGroupCoordinateSet
            fields = {
                "uuid": ["exact"],
                "updated": ["lt", "gt"],
                "workflow_job_group": ["exact"],
                "user_agent": ["exact", "icontains"],
                "created": ["lt", "gt"],
            }


class WorkflowJobGroupCoordinateSetDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Performs operations on a single WorkflowJobGroupCoordinateSet instance.
    """

    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions)
    _ignore_model_permissions = True
    queryset = WorkflowJobGroupCoordinateSet.objects.all()
    serializer_class = WorkflowJobGroupCoordinateSetSerializer
