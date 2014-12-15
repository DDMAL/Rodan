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
    - `output_ports` -- POST-only. Hyperlinks of OutputPorts. If not provided, Rodan
      will select the ones that has no outgoing Connections by default.
    - `include_failed_runjobs` -- POST-only. If set, ResultsPackage will include
      failed error messages of RunJobs.
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

        include_failed_runjobs = 'include_failed_runjobs' in self.request.data
        registry.tasks['rodan.core.package_results'].apply_async((rp_id, include_failed_runjobs))


class ResultsPackageDetail(generics.RetrieveDestroyAPIView):
    """
    Perform operations on a single ResultsPackage instance.

    #### Parameters

    - `status` -- PATCH-only. Only valid as cancellation of the ResultsPackage.
    """
    model = ResultsPackage
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ResultsPackageSerializer
    queryset = ResultsPackage.objects.all()  # [TODO] filter for current user?

    def patch(self, request, *args, **kwargs):
        rp = self.get_object()
        old_status = rp.status
        new_status = request.data.get('status', None)

        if old_status in (task_status.SCHEDULED, task_status.PROCESSING) and new_status == task_status.CANCELLED:
            revoke(rp.celery_task_id, terminate=True)
            serializer = self.get_serializer(rp, data={'status': task_status.CANCELLED}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        elif new_status is not None:
            raise CustomAPIException({'status': ["Invalid status update"]}, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise CustomAPIException({'status': ["Invalid update"]}, status=status.HTTP_400_BAD_REQUEST)

    def perform_destroy(self, instance):
        if instance.status in (task_status.SCHEDULED, task_status.PROCESSING):
            raise CustomAPIException("Please cancel the processing of this package before deleting.", status=status.HTTP_400_BAD_REQUEST)
        instance.delete()
