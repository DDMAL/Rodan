from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from celery import registry
from celery.task.control import revoke

from django.db.models import Q
import django_filters

from rodan.models.runjob import RunJob
from rodan.serializers.runjob import RunJobSerializer
from rodan.constants import task_status
from rodan.exceptions import CustomAPIException

class RunJobList(generics.ListAPIView):
    """
    Returns a list of all RunJobs. Do not accept POST request as RunJobs are typically created by the server.
    """
    model = RunJob
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = RunJobSerializer
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

    #### Parameters
    - `status` -- PATCH-only. An integer. Only (Finished, Failed, Waiting for input, Processing) -> Scheduled,
      to redo a RunJob and its downstream RunJobs.
    """
    model = RunJob
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = RunJobSerializer
    queryset = RunJob.objects.all() # [TODO] filter according to the user?

    def patch(self, request, *a, **k):
        rj = self.get_object()
        old_status = rj.status
        new_status = request.data.get('status', None)

        if old_status not in (task_status.FINISHED, task_status.FAILED, task_status.WAITING_FOR_INPUT, task_status.PROCESSING) or new_status != task_status.SCHEDULED:
            raise CustomAPIException({'status': ["Invalid status update"]}, status=status.HTTP_400_BAD_REQUEST)
        else:
            self._reset_runjob_tree(rj)
            wfrun = rj.workflow_run
            registry.tasks['rodan.core.master_task'].apply_async((wfrun.uuid.hex,))

            wfrun.status = task_status.RETRYING
            wfrun.save(update_fields=['status'])
            updated_rj = self.get_object()  # refetch
            serializer = self.get_serializer(updated_rj)
            return Response(serializer.data)

    def _reset_runjob_tree(self, rj):
        """
        rj -- expected status should not be SCHEDULED.
        """
        if rj.celery_task_id is not None:
            revoke(rj.celery_task_id, terminate=True)

        # 1. Revoke all downstream runjobs
        for o in rj.outputs.all():
            r = o.resource
            for i in r.inputs.filter(Q(run_job__workflow_run=rj.workflow_run) & ~Q(run_job__status=task_status.SCHEDULED)):
                self._reset_runjob_tree(i.run_job)

            # 2. Clear output resources
            r.compat_resource_file = None
            r.has_thumb = False
            r.save(update_fields=['compat_resource_file', 'has_thumb'])

        # 3. Reset status and clear interactive data
        original_settings = {}
        for k, v in rj.job_settings.iteritems():
            if not k.startswith('@'):
                original_settings[k] = v
        rj.job_settings = original_settings
        rj.status = task_status.SCHEDULED
        rj.save(update_fields=['status', 'job_settings'])
