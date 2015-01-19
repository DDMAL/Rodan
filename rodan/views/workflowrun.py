import urlparse
import os
import shutil
from operator import itemgetter
from celery import registry, chain
from celery.task.control import revoke
from django.core.urlresolvers import resolve

from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from rodan.models import Workflow, RunJob, WorkflowJob, WorkflowRun, Connection, ResourceAssignment, Resource, Input, Output, OutputPort, InputPort, ResourceType
from rodan.serializers.user import UserSerializer
from rodan.paginators.pagination import PaginationSerializer
from rodan.serializers.workflowrun import WorkflowRunSerializer, WorkflowRunByPageSerializer

from rodan.constants import task_status
from rodan.exceptions import CustomAPIException

class WorkflowRunList(generics.ListCreateAPIView):
    """
    Returns a list of all WorkflowRuns. Accepts a POST request with a data body to
    create a new WorkflowRun. POST requests will return the newly-created WorkflowRun
    object.

    Creating a new WorkflowRun instance executes the workflow. Meanwhile, RunJobs,
    Inputs, Outputs and Resources are created corresponding to the workflow.

    #### Parameters
    - `workflow` -- GET-only. UUID(GET) or Hyperlink(POST) of a Workflow.
    """
    model = WorkflowRun
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = WorkflowRunSerializer
    pagination_serializer_class = PaginationSerializer
    filter_fields = ('workflow', 'project')
    queryset = WorkflowRun.objects.all()  # [TODO] filter according to the user?

    def perform_create(self, serializer):
        wfrun_status = serializer.validated_data.get('status', task_status.PROCESSING)
        if wfrun_status != task_status.PROCESSING:
            raise ValidationError({'status': ["Cannot create a cancelled, failed or finished WorkflowRun."]})
        wf = serializer.validated_data['workflow']
        if not wf.valid:
            raise ValidationError({'workflow': ["Workflow must be valid before you can run it."]})

        wfrun = serializer.save(creator=self.request.user, project=wf.project, workflow_name=wf.name)
        wfrun_id = str(wfrun.uuid)
        test_run = serializer.validated_data.get('test_run', False)
        self._create_workflow_run(wf, wfrun, test_run)
        registry.tasks['rodan.core.master_task'].apply_async((wfrun_id,))

    def _create_workflow_run(self, workflow, workflow_run, test_run):
        endpoint_workflowjobs = self._endpoint_workflow_jobs(workflow)
        singleton_workflowjobs = self._singleton_workflow_jobs(workflow)
        workflowjob_runjob_map = {}

        rc_multiple = None
        for rc in workflow.resource_collections.all():
            if rc.resources.count() > 1:
                rc_multiple = rc

        if rc_multiple:
            resources = rc_multiple.resources.all()
            for res in resources:
                self._runjob_creation_loop(endpoint_workflowjobs, singleton_workflowjobs, workflowjob_runjob_map, workflow_run, res)
                if test_run:
                    break
        else:
            self._runjob_creation_loop(endpoint_workflowjobs, singleton_workflowjobs, workflowjob_runjob_map, workflow_run, None)

    def _runjob_creation_loop(self, endpoint_workflowjobs, singleton_workflowjobs, workflowjob_runjob_map, workflow_run, arg_resource):
        for wfjob in endpoint_workflowjobs:
            self._create_runjobs(wfjob, workflowjob_runjob_map, workflow_run, arg_resource)

        workflow_job_iteration = {}

        for wfjob in workflowjob_runjob_map:
            workflow_job_iteration[wfjob] = workflowjob_runjob_map[wfjob]

        for wfjob in workflow_job_iteration:
            if wfjob not in singleton_workflowjobs:
                del workflowjob_runjob_map[wfjob]

    def _create_runjobs(self, wfjob_A, workflowjob_runjob_map, workflow_run, arg_resource):
        if wfjob_A in workflowjob_runjob_map:
            return workflowjob_runjob_map[wfjob_A]

        runjob_A = self._create_runjob_A(wfjob_A, workflow_run, arg_resource)

        incoming_connections = Connection.objects.filter(input_port__workflow_job=wfjob_A)

        for conn in incoming_connections:
            wfjob_B = conn.output_workflow_job
            runjob_B = self._create_runjobs(wfjob_B, workflowjob_runjob_map, workflow_run, arg_resource)

            associated_output = Output.objects.get(output_port=conn.output_port,
                                                   run_job=runjob_B)

            Input(run_job=runjob_A,
                  input_port=conn.input_port,
                  input_port_type_name=conn.input_port.input_port_type.name,
                  resource=associated_output.resource).save()

        # entry inputs
        for ip in InputPort.objects.filter(workflow_job=wfjob_A):
            try:
                ra = ResourceAssignment.objects.get(input_port=ip)
            except ResourceAssignment.DoesNotExist:
                ra = None

            if ra:
                if ra.resource_collection:
                    if ra.resource_collection.resources.count() > 1:
                        entry_res = arg_resource
                    else:
                        entry_res = ra.resource_collection.resources.first()
                else:
                    entry_res = ra.resource

                Input(run_job=runjob_A,
                      input_port=ra.input_port,
                      input_port_type_name=ra.input_port.input_port_type.name,
                      resource=entry_res).save()

        # Determine ResourceType of the outputs of RunJob A.
        for o in runjob_A.outputs.all():
            resource_type_set = set(o.output_port.output_port_type.resource_types.all())
            res = o.resource

            if len(resource_type_set) > 1:
                ## Eliminate this set by considering the connected InputPorts
                for connection in o.output_port.connections.all():
                    in_type_set = set(connection.input_port.input_port_type.resource_types.all())
                    resource_type_set.intersection_update(in_type_set)

            if len(resource_type_set) > 1:
                ## Try to find a same resource type in the input resources.
                for i in runjob_A.inputs.all():
                    if i.resource.resource_type in resource_type_set:
                        res.resource_type = i.resource.resource_type
                        break
                else:
                    res.resource_type = resource_type_set.pop()
            else:
                res.resource_type = resource_type_set.pop()
            res.save()

        workflowjob_runjob_map[wfjob_A] = runjob_A
        return runjob_A

    def _create_runjob_A(self, wfjob, workflow_run, arg_resource):
        run_job = RunJob(workflow_job=wfjob,
                         workflow_job_uuid=wfjob.uuid.hex,
                         resource_uuid=arg_resource.uuid.hex if arg_resource else None,
                         workflow_run=workflow_run,
                         job_name=wfjob.job.job_name,
                         job_settings=wfjob.job_settings)
        run_job.save()

        outputports = OutputPort.objects.filter(workflow_job=wfjob).prefetch_related('output_port_type__resource_types')

        for op in outputports:
            resource = Resource(project=workflow_run.workflow.project,
                                resource_type=ResourceType.cached('application/octet-stream'))  # ResourceType will be determined later (see method _create_runjobs)
            resource.save()

            output = Output(output_port=op,
                            run_job=run_job,
                            resource=resource,
                            output_port_type_name=op.output_port_type.name)
            output.save()

            if arg_resource:   # resource collection identifier
                resource.name = arg_resource.name
            else:
                resource.name = 'Output of workflow {0}'.format(workflow_run.workflow_name)  # assign a name for it
            resource.origin = output
            resource.save()

        return run_job

    def _endpoint_workflow_jobs(self, workflow):
        workflow_jobs = WorkflowJob.objects.filter(workflow=workflow)
        endpoint_workflowjobs = []

        for wfjob in workflow_jobs:
            connections = Connection.objects.filter(output_port__workflow_job=wfjob)

            if not connections:
                endpoint_workflowjobs.append(wfjob)

        return endpoint_workflowjobs

    def _singleton_workflow_jobs(self, workflow):
        singleton_workflowjobs = []

        for wfjob in WorkflowJob.objects.filter(workflow=workflow):
            singleton_workflowjobs.append(wfjob)

        resource_collections = workflow.resource_collections.all()
        for rc in resource_collections:
            if rc.resources.count() > 1:
                for ra in rc.resource_assignments.all():
                    initial_wfjob = WorkflowJob.objects.get(input_ports=ra.input_port)
                    self._traversal(singleton_workflowjobs, initial_wfjob)

        return singleton_workflowjobs

    def _traversal(self, singleton_workflowjobs, wfjob):
        if wfjob in singleton_workflowjobs:
            singleton_workflowjobs.remove(wfjob)
        adjacent_connections = Connection.objects.filter(output_port__workflow_job=wfjob)
        for conn in adjacent_connections:
            wfjob = WorkflowJob.objects.get(input_ports=conn.input_port)
            self._traversal(singleton_workflowjobs, wfjob)


class WorkflowRunDetail(generics.RetrieveAPIView):
    """
    Performs operations on a single WorkflowRun instance.

    #### Parameters
    - `status` -- PATCH-only. An integer. Attempt of uncancelling will trigger an error.
    """
    model = WorkflowRun
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = WorkflowRunSerializer
    queryset = WorkflowRun.objects.all() # [TODO] filter according to the user?

    def patch(self, request, *args, **kwargs):
        wfrun = self.get_object()
        old_status = wfrun.status
        new_status = request.data.get('status', None)

        if old_status in (task_status.PROCESSING, task_status.RETRYING) and new_status == task_status.CANCELLED:
            runjobs_to_revoke_query = RunJob.objects.filter(workflow_run=wfrun, status__in=(task_status.SCHEDULED, task_status.PROCESSING, task_status.WAITING_FOR_INPUT))
            runjobs_to_revoke_celery_id = runjobs_to_revoke_query.values_list('celery_task_id', flat=True)

            for celery_id in runjobs_to_revoke_celery_id:
                if celery_id is not None:
                    revoke(celery_id, terminate=True)
            runjobs_to_revoke_query.update(status=task_status.CANCELLED)

            serializer = self.get_serializer(wfrun, data={'status': task_status.CANCELLED}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        elif old_status in (task_status.CANCELLED, task_status.FAILED) and new_status == task_status.RETRYING:
            runjobs_to_retry_query = RunJob.objects.filter(workflow_run=wfrun, status__in=(task_status.FAILED, task_status.CANCELLED))
            for rj in runjobs_to_retry_query:
                rj.status = task_status.SCHEDULED
                rj.error_summary = ''
                rj.error_details = ''
                original_settings = {}
                for k, v in rj.job_settings.iteritems():
                    if not k.startswith('@'):
                        original_settings[k] = v
                rj.job_settings = original_settings
                rj.save(update_fields=['status', 'job_settings', 'error_summary', 'error_details'])

            registry.tasks['rodan.core.master_task'].apply_async((wfrun.uuid.hex,))

            serializer = self.get_serializer(wfrun, data={'status': task_status.RETRYING}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        elif new_status is not None:
            raise CustomAPIException({'status': ["Invalid status update"]}, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise CustomAPIException({'status': ["Invalid update"]}, status=status.HTTP_400_BAD_REQUEST)
