from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from celery import registry
from celery.task.control import revoke

import django_filters

from rodan.models.runjob import RunJob
from rodan.serializers.runjob import RunJobSerializer
from rodan.constants import task_status
from rodan.exceptions import CustomAPIException

class RunJobList(generics.ListAPIView):
    """
    Returns a list of all RunJobs. Do not accept POST request as RunJobs are typically created by the server.

    #### Parameters
    - `status` -- GET-only. Status number.
    - `project` -- GET-only. UUID of a Project.
    - `workflow_run` -- GET-only. UUID of a WorkflowRun.
    """
    model = RunJob
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = RunJobSerializer
    queryset = RunJob.objects.all() # [TODO] filter according to the user?

    class filter_class(django_filters.FilterSet):
        project = django_filters.CharFilter(name="workflow_run__project")
        class Meta:
            model = RunJob
            fields = ('status', 'project', 'workflow_run')


class RunJobDetail(generics.RetrieveAPIView):
    """
    Performs operations on a single RunJob instance.

    #### Parameters
    - `status` -- PATCH-only. An integer. Only Finished -> Scheduled --- to redo a
      RunJob and its downstream RunJobs.
    """
    model = RunJob
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = RunJobSerializer
    queryset = RunJob.objects.all() # [TODO] filter according to the user?

    def patch(self, request, *a, **k):
        rj = self.get_object()
        old_status = rj.status
        new_status = request.data.get('status', None)

        if old_status != task_status.FINISHED or new_status != task_status.SCHEDULED:
            raise CustomAPIException({'status': ["Invalid status update"]}, status=status.HTTP_400_BAD_REQUEST)
        else:
            self._reset_runjob_tree(rj)
            wfrun = rj.workflow_run
            registry.tasks['rodan.core.master_task'].apply_async((wfrun.uuid.hex,))
            wfrun.status = task_status.RETRYING
            wfrun.save(update_fields=['status'])
            updated_rj = self.get_object()
            serializer = self.get_serializer(updated_rj)
            return Response(serializer.data)

    def _reset_runjob_tree(self, rj):
        if rj.celery_task_id is not None:
            revoke(rj.celery_task_id, terminate=True)
        if rj.status != task_status.SCHEDULED:
            rj.status = task_status.SCHEDULED

            # clear interactive data
            original_settings = {}
            for k, v in rj.job_settings.iteritems():
                if not k.startswith('@'):
                    original_settings[k] = v
            rj.job_settings = original_settings

            rj.save(update_fields=['status', 'job_settings'])
            for o in rj.outputs.all():
                r = o.resource
                r.compat_resource_file = None
                r.save(update_fields=['compat_resource_file'])
                for i in r.inputs.filter(run_job__workflow_run=rj.workflow_run):
                    self._reset_runjob_tree(i.run_job)
