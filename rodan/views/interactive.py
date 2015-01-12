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

    def get(self, request, run_job_uuid, *a, **k):
        # check runjob
        runjob = get_object_or_404(RunJob, uuid=run_job_uuid)
        if runjob.status != task_status.WAITING_FOR_INPUT:
            return Response({'message': 'This RunJob does not accept input now'}, status=status.HTTP_400_BAD_REQUEST)

        manual_task = registry.tasks[str(runjob.job_name)]
        template, context = manual_task.get_interface(run_job_uuid)
        c = RequestContext(request, context)
        return HttpResponse(template.render(c))

    def post(self, request, run_job_uuid, *a, **k):
        # check runjob
        runjob = get_object_or_404(RunJob, uuid=run_job_uuid)
        if runjob.status != task_status.WAITING_FOR_INPUT:
            return Response({'message': 'This RunJob does not accept input now'}, status=status.HTTP_400_BAD_REQUEST)

        if isinstance(request.data, dict) and "__serialized__" in request.data:
            user_input = json.loads(request.data['__serialized__'])
        else:
            user_input = request.data

        manual_task = registry.tasks[str(runjob.job_name)]
        try:
            settings_update = manual_task.validate_user_input(run_job_uuid, user_input)
        except APIException as e:
            raise e

        runjob.status = task_status.SCHEDULED
        runjob.error_summary = ''
        runjob.error_details = ''
        runjob.job_settings.update(settings_update)
        runjob.save()

        # call master_task to continue workflowrun
        registry.tasks['rodan.core.master_task'].apply_async((runjob.workflow_run.uuid,))
        return Response(status=status.HTTP_200_OK)
