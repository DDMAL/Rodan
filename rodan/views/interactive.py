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
from rest_framework import permissions
from rest_framework.exceptions import APIException
from rodan.models import RunJob, Input, Resource
from rodan.constants import task_status


class InteractiveView(APIView):
    """
    Rodan makes available interfaces for interactive jobs. Each endpoint accepts
    GET and POST requests.

    #### Parameters
    - `**kwargs` -- POST-only. Job settings.
    """
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, run_job_uuid, *a, **k):
        # check runjob
        runjob = get_object_or_404(RunJob, uuid=run_job_uuid)
        if not runjob.ready_for_input:
            return Response({'message': 'This RunJob does not accept input now'}, status=status.HTTP_400_BAD_REQUEST)

        manual_task = registry.tasks[str(runjob.workflow_job.job.job_name)]
        template, context = manual_task.get_interface(run_job_uuid)
        c = RequestContext(request, context)
        return HttpResponse(template.render(c))

    def post(self, request, run_job_uuid, *a, **k):
        # check runjob
        runjob = get_object_or_404(RunJob, uuid=run_job_uuid)
        if not runjob.ready_for_input:
            return Response({'message': 'This RunJob does not accept input now'}, status=status.HTTP_400_BAD_REQUEST)

        manual_task = registry.tasks[str(runjob.workflow_job.job.job_name)]
        try:
            manual_task.save_user_input(run_job_uuid, request.DATA)
        except APIException as e:
            raise e

        runjob.ready_for_input = False
        runjob.status = task_status.FINISHED
        runjob.error_summary = ''
        runjob.error_details = ''
        runjob.save()

        # call master_task to continue workflowrun
        registry.tasks['rodan.core.master_task'].apply_async((runjob.workflow_run.uuid,))
        return Response(status=status.HTTP_200_OK)
