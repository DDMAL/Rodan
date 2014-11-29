import json, tempfile
from celery import registry
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.template import RequestContext
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rodan.models import RunJob, Input, Resource
from rodan.models.runjob import RunJobStatus
from rodan.jobs.master_task import master_task


class InteractiveView(APIView):
    """
    Rodan makes available interfaces for interactive jobs. Each endpoint accepts
    GET and POST requests.

    #### Parameters
    - `**kwargs` -- POST-only. Job settings.
    """
    def get(self, request, run_job_uuid, *a, **k):
        # check runjob
        runjob = get_object_or_404(RunJob, uuid=run_job_uuid)
        if runjob.workflow_run.cancelled:
            return Response({'message': 'WorkflowRun has been cancelled'}, status=status.HTTP_400_BAD_REQUEST)
        if not runjob.ready_for_input:
            return Response({'message': 'This RunJob does not accept input now'}, status=status.HTTP_400_BAD_REQUEST)

        manual_task = registry.tasks[str(runjob.workflow_job.job.job_name)]
        template, context = manual_task.get_interface(run_job_uuid)
        c = RequestContext(request, context)
        return HttpResponse(template.render(c))

    def post(self, request, run_job_uuid, *a, **k):
        # check runjob
        runjob = get_object_or_404(RunJob, uuid=run_job_uuid)
        if runjob.workflow_run.cancelled:
            return Response({'message': 'WorkflowRun has been cancelled'}, status=status.HTTP_400_BAD_REQUEST)
        if not runjob.ready_for_input:
            return Response({'message': 'This RunJob does not accept input now'}, status=status.HTTP_400_BAD_REQUEST)

        manual_task = registry.tasks[str(runjob.workflow_job.job.job_name)]
        try:
            manual_task.save_user_input(run_job_uuid, request.DATA)
        except APIException as e:
            raise e

        runjob.ready_for_input = False
        runjob.status = RunJobStatus.HAS_FINISHED
        runjob.error_summary = ''
        runjob.error_details = ''
        runjob.save()

        # call master_task to continue workflowrun
        master_task.apply_async((runjob.workflow_run.uuid,))
        return Response(status=status.HTTP_200_OK)
