from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from celery import registry
from celery.task.control import revoke
from django.core.urlresolvers import resolve, Resolver404

from rodan.serializers.resultspackage import ResultsPackageSerializer, ResultsPackageListSerializer
from rodan.models import ResultsPackage
from rodan.constants import task_status
from rodan.exceptions import CustomAPIException


class ResultsPackageList(generics.ListCreateAPIView):
    """
    Returns a list of all ResultsPackages. Accepts a POST request with a data body to
    create a new ResultsPackage. POST requests will return the newly-created
    ResultsPackage object.

    Creating a new ResultsPackage instance starts the background packaging task.

    #### Parameters
    - `creator` -- GET-only. UUID of a User.
    - `workflow_run` -- GET & POST. UUID(GET) or Hyperlink(POST) of a WorkflowRun.
    - `output_ports` -- POST-only. Hyperlinks of OutputPorts.
    """
    model = ResultsPackage
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ResultsPackageListSerializer
    queryset = ResultsPackage.objects.all()  # [TODO] filter for current user?
    filter_fields = ('creator', 'workflow_run')

    def perform_create(self, serializer):
        # check status
        rp = serializer.save(creator=self.request.user) # expiry_date
        rp_id = str(rp.uuid)

        registry.tasks['rodan.core.package_results'].apply_async((rp_id, True)) # TODO


class ResultsPackageDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Perform operations on a single ResultsPackage instance.
    """
    model = ResultsPackage
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ResultsPackageSerializer
    queryset = ResultsPackage.objects.all()  # [TODO] filter for current user?

    def perform_update(self, serializer):
        rp_id = serializer.data['uuid']
        rp = ResultsPackage.objects.get(uuid=rp_id)
        old_status = rp.status
        new_status = serializer.validated_data.get('status', None)

        if old_status in (task_status.SCHEDULED, task_status.PROCESSING) and new_status == task_status.CANCELLED:
            revoke(rp.celery_task_id, terminate=True)
        elif new_status is not None:
            raise ValidationError({'status': ["Invalid status update"]})

        serializer.save()

    def perform_destroy(self, instance):
        if instance.status in (task_status.SCHEDULED, task_status.PROCESSING):
            raise CustomAPIException("Please cancel the processing of this package before deleting.", status=status.HTTP_400_BAD_REQUEST)
        instance.delete()
