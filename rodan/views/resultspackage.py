import datetime
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from celery import registry
from celery.task.control import revoke
from django.conf import settings
from django.utils import timezone
import django_filters

from rodan.serializers.resultspackage import ResultsPackageListSerializer
from rodan.models import ResultsPackage
from rodan.constants import task_status
from rodan.exceptions import CustomAPIException
from rodan.permissions import CustomObjectPermissions


class ResultsPackageList(generics.ListCreateAPIView):
    """
    Returns a list of all ResultsPackages. Accepts a POST request with a data body to
    create a new ResultsPackage. POST requests will return the newly-created
    ResultsPackage object.

    Creating a new ResultsPackage instance starts the background packaging task.

    #### Other Parameters
    - `workflow_run` -- GET & POST. UUID(GET) or Hyperlink(POST) of a WorkflowRun.
    """
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions, )
    _ignore_model_permissions = True
    queryset = ResultsPackage.objects.all()
    serializer_class = ResultsPackageListSerializer

    class filter_class(django_filters.FilterSet):
        project = django_filters.CharFilter(name="workflow_run__project")
        class Meta:
            model = ResultsPackage
            fields = {
                "status": ['exact'],
                "expiry_time": ['lt', 'gt'],
                "uuid": ['exact'],
                "created": ['lt', 'gt'],
                "workflow_run": ['exact'],
                "creator": ['exact'],
                "percent_completed": ['lt', 'gt'],
                "packaging_mode": ['exact']
            }

    def perform_create(self, serializer):
        rp_status = serializer.validated_data.get('status', task_status.PROCESSING)
        if rp_status != task_status.PROCESSING:
            raise ValidationError({'status': ["Cannot create a cancelled, failed, finished or expired ResultsPackage."]})

        auto_expiry_seconds = settings.RODAN_RESULTS_PACKAGE_AUTO_EXPIRY_SECONDS
        now = timezone.now()
        if auto_expiry_seconds:
            user_set_expiry_time = serializer.validated_data.get('expiry_time')
            if not user_set_expiry_time:
                if self.request.user.is_staff: # [TODO] which users do we allow to create never-expire packages?
                    expiry_time = None
                else:
                    decided_expiry = auto_expiry_seconds
                    expiry_time = now + datetime.timedelta(seconds=decided_expiry)
            else:
                user_set_expiry_seconds = (user_set_expiry_time - now).total_seconds()
                if user_set_expiry_seconds > auto_expiry_seconds:
                    decided_expiry = auto_expiry_seconds
                else:
                    decided_expiry = user_set_expiry_seconds
                expiry_time = now + datetime.timedelta(seconds=decided_expiry)

            rp = serializer.save(creator=self.request.user,
                                 expiry_time=expiry_time)
        else:
            rp = serializer.save(creator=self.request.user,
                                 expiry_time=None)
        rp_id = rp.uuid.hex

        registry.tasks['rodan.core.package_results'].apply_async((rp_id, ))

class ResultsPackageDetail(generics.RetrieveDestroyAPIView):
    """
    Perform operations on a single ResultsPackage instance.

    #### Parameters

    - `status` -- PATCH-only. Only valid as cancellation of the ResultsPackage.
    """
    permission_classes = (permissions.IsAuthenticated, CustomObjectPermissions, )
    _ignore_model_permissions = True
    queryset = ResultsPackage.objects.all()
    serializer_class = ResultsPackageListSerializer

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
        if instance.celery_task_id:
            revoke(instance.celery_task_id, terminate=True)  # revoke scheduled expiry task
        instance.delete()
