import json, tempfile, inspect, os, mimetypes
from celery import registry
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.template import RequestContext
from django.http import HttpResponse, Http404
from django.conf import settings
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
    authentication_classes = ()

    def get(self, request, run_job_uuid, additional_url, *a, **k):
        # check runjob
        runjob = get_object_or_404(RunJob, uuid=run_job_uuid)
        if runjob.status != task_status.WAITING_FOR_INPUT:
            return Response({'message': 'This RunJob does not accept input now'}, status=status.HTTP_400_BAD_REQUEST)

        manual_task = registry.tasks[str(runjob.job_name)]

        if not additional_url:
            # request for the interface
            template, context = manual_task.get_interface(run_job_uuid)
            c = RequestContext(request, context)
            return HttpResponse(template.render(c))
        else:
            # request for static files
            ## find the path of the static file. Need to figure out the vendor module
            job_vendor_path = manual_task._vendor_path()
            job_static_path = os.path.join(job_vendor_path, 'static')  # e.g.: "/path/to/rodan/jobs/gamera/static"
            if os.path.isabs(additional_url) or additional_url == '..' or additional_url.startswith('../'):  # prevent traversal (from flask https://github.com/mitsuhiko/flask/blob/master/flask/helpers.py#L567-L591)
                raise Http404
            abspath = os.path.join(job_static_path, additional_url)

            with open(abspath, 'rb') as fsock:
                mime_type = mimetypes.guess_type(abspath)[0]
                return HttpResponse(fsock, content_type=mime_type)

    def post(self, request, run_job_uuid, additional_url, *a, **k):
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
            setattr(manual_task, 'url', additional_url)  # HACK
            retval = manual_task.validate_user_input(run_job_uuid, user_input)
            del manual_task.url
        except APIException as e:
            raise e

        if isinstance(retval, manual_task.WAITING_FOR_INPUT):
            settings_update = retval.settings_update
            runjob.job_settings.update(settings_update)
            runjob.save()
            if retval.response:
                return HttpResponse(retval.response, status=status.HTTP_200_OK)
        else:
            settings_update = retval
            runjob.status = task_status.SCHEDULED
            runjob.error_summary = ''
            runjob.error_details = ''
            runjob.job_settings.update(settings_update)
            runjob.save()
            # call master_task to continue workflowrun
            registry.tasks['rodan.core.master_task'].apply_async((runjob.workflow_run.uuid,))
        return Response(status=status.HTTP_200_OK)
