import json
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
from rodan.models import RunJob, Input
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

        # read input values: urls, actual path, and type
        input_values = Input.objects.filter(run_job__pk=run_job_uuid).values(
            'input_port__input_port_type__name',
            'resource__compat_resource_file',
            'resource__resource_type__mimetype',
            'resource__uuid')
        inputs = {}
        for input_value in input_values:
            ipt_name = input_value['input_port__input_port_type__name']
            if ipt_name not in inputs:
                inputs[ipt_name] = []
            r = Resource.objects.get(input_value['resource__uuid'])
            inputs[ipt_name].append({
                'resource_path': input_value['resource__compat_resource_file'],
                'resource_type': input_value['resource__resource_type__mimetype'],
                'resource_url': r.compat_file_url,
                'small_thumb_url': r.small_thumb_url,
                'medium_thumb_url': r.medium_thumb_url,
                'large_thumb_url': r.large_thumb_url
            })
        settings = runjob.job_settings
        manual_task = registry.tasks[str(runjob.workflow_job.job.job_name)]
        template, context = manual_task.get_my_interface(inputs, settings)
        c = RequestContext(request, context)
        return HttpResponse(template.render(c))

    def post(self, request, run_job_uuid, *a, **k):
        # check runjob
        runjob = get_object_or_404(RunJob, uuid=run_job_uuid)
        if runjob.workflow_run.cancelled:
            return Response({'message': 'WorkflowRun has been cancelled'}, status=status.HTTP_400_BAD_REQUEST)
        if not runjob.ready_for_input:
            return Response({'message': 'This RunJob does not accept input now'}, status=status.HTTP_400_BAD_REQUEST)
        userdata = {}
        for k, v in request.POST.iteritems():
            userdata[k] = v

        # read input values: actual path, and type
        input_values = Input.objects.filter(run_job__pk=run_job_uuid).values(
            'input_port__input_port_type__name',
            'resource__compat_resource_file',
            'resource__resource_type__mimetype')
        inputs = {}
        for input_value in input_values:
            ipt_name = input_value['input_port__input_port_type__name']
            if ipt_name not in inputs:
                inputs[ipt_name] = []
            inputs[ipt_name].append({
                'resource_path': input_value['resource__compat_resource_file'],
                'resource_type': input_value['resource__resource_type__mimetype'],
            })
        settings = runjob.job_settings
        manual_task = registry.tasks[str(runjob.workflow_job.job.job_name)]
        try:
            manual_task.validate_my_userdata(inputs, settings, userdata)
        except APIException as e:
            raise e

        runjob.needs_input = False
        runjob.ready_for_input = False
        runjob.status = RunJobStatus.HAS_FINISHED
        runjob.error_summary = ''
        runjob.error_details = ''
        runjob.save()
        resource = runjob.outputs.first().resource
        resource.compat_resource_file.save('', ContentFile(json.dumps(userdata)))

        # call master_task to continue workflowrun
        master_task.apply_async((runjob.workflow_run.uuid,))
        return Response(status=status.HTTP_200_OK)
