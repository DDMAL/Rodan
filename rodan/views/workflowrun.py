import urlparse
import os
import shutil
from operator import itemgetter
from celery import registry, chain
from django.core.urlresolvers import resolve

from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.relations import HyperlinkedIdentityField

from rodan.models import Workflow, RunJob, WorkflowJob, WorkflowRun, Connection, Resource, Input, Output, OutputPort, InputPort, ResourceType
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

    #### Other Parameters
    - `workflow` -- GET & POST. UUID(GET) or Hyperlink(POST) of a Workflow.
    - `resource_assignments` -- POST-only. A JSON object. Keys are URLs of InputPorts
      in the Workflow, and values are list of Resource URLs.
    """
    model = WorkflowRun
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = WorkflowRunSerializer
    pagination_serializer_class = PaginationSerializer
    filter_fields = {
        "status": ['exact'],
        "updated": ['lt', 'gt'],
        "uuid": ['exact'],
        "workflow": ['exact'],
        "created": ['lt', 'gt'],
        "project": ['exact'],
        "creator": ['exact'],
        "name": ['exact', 'icontains']
    }
    queryset = WorkflowRun.objects.all()  # [TODO] filter according to the user?

    def perform_create(self, serializer):
        wfrun_status = serializer.validated_data.get('status', task_status.PROCESSING)
        if wfrun_status != task_status.PROCESSING:
            raise ValidationError({'status': ["Cannot create a cancelled, failed or finished WorkflowRun."]})
        wf = serializer.validated_data['workflow']
        if not wf.valid:
            raise ValidationError({'workflow': ["Workflow must be valid before you can run it."]})

        if 'resource_assignments' not in self.request.data:
            raise ValidationError({'resource_assignments': ['This field is required']})
        resource_assignment_dict = self.request.data['resource_assignments']

        try:
            validated_resource_assignment_dict = self._validate_resource_assignments(resource_assignment_dict, serializer)
        except ValidationError as e:
            e.detail = {'resource_assignments': e.detail}
            raise e

        wfrun = serializer.save(creator=self.request.user, project=wf.project)
        wf_id = str(wf.uuid)
        wfrun_id = str(wfrun.uuid)
        registry.tasks['rodan.core.create_workflowrun'].apply_async((wf_id, wfrun_id, validated_resource_assignment_dict))


    def _validate_resource_assignments(self, resource_assignment_dict, serializer):
        """
        Validates the resource assignments

        May throw ValidationError.
        Returns a validated dictionary.
        """
        if not isinstance(resource_assignment_dict, dict):
            raise ValidationError(['This field must be a JSON object'])

        unsatisfied_ips = set(InputPort.objects.filter(workflow_job__in=serializer.validated_data['workflow'].workflow_jobs.all(), connections__isnull=True))
        validated_resource_assignment_dict = {}
        multiple_resource_set = None
        for input_port, resources in resource_assignment_dict.iteritems():
            # 1. InputPort is not satisfied
            h_ip = HyperlinkedIdentityField(view_name="inputport-detail")
            h_ip.queryset = InputPort.objects.all()
            try:
                ip = h_ip.to_internal_value(input_port)
            except ValidationError as e:
                e.detail = {input_port: e.detail}
                raise e

            if ip not in unsatisfied_ips:
                raise ValidationError({input_port: ['Assigned InputPort must be unsatisfied']})
            unsatisfied_ips.remove(ip)
            types_of_ip = ip.input_port_type.resource_types.all()

            # 2. Resources:
            if not isinstance(resources, list):
                raise ValidationError({input_port: ['A list of resources is expected']})

            h_res = HyperlinkedIdentityField(view_name="resource-detail")
            h_res.queryset = Resource.objects.all()
            ress = []

            for index, r in enumerate(resources):
                try:
                    ress.append(h_res.to_internal_value(r))
                except ValidationError as e:
                    e.detail = {input_port: {index: e.detail}}
                    raise e


            ## No empty resource set
            if len(ress) == 0:
                raise ValidationError({input_port: ['It is not allowed to assign an empty resource set']})

            ## There must be at most one multiple resource set
            if len(ress) > 1:
                ress_set = set(map(lambda r: r.uuid, ress))
                if not multiple_resource_set:
                    multiple_resource_set = ress_set
                else:
                    if multiple_resource_set != ress_set:
                        raise ValidationError({input_port: ['It is not allowed to assign multiple resource sets']})

            ## Resource must be in project and resource types are matched
            for index, res in enumerate(ress):
                if res.project != serializer.validated_data['workflow'].project:
                    raise ValidationError({input_port: {index: ['Resource is not in the project of Workflow']}})

                if not res.compat_resource_file:
                    raise ValidationError({input_port: {index: ['The compatible resource file is not ready']}})

                type_of_res = res.resource_type
                if type_of_res not in types_of_ip:
                    raise ValidationError({input_port: {index: ['The resource type does not match the InputPort']}})

            validated_resource_assignment_dict[ip] = ress

        # Still we have unsatisfied input ports
        if unsatisfied_ips:
            raise ValidationError(['There are still unsatisfied InputPorts: {0}'.format(
                ' '.join([h_ip.get_url(ip, 'inputport-detail', self.request, None) for ip in unsatisfied_ips])
            )])

        return validated_resource_assignment_dict



class WorkflowRunDetail(mixins.UpdateModelMixin, generics.RetrieveAPIView):
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

        if new_status:
            if old_status in (task_status.PROCESSING, task_status.RETRYING, task_status.FAILED) and new_status == task_status.CANCELLED:
                response = self.partial_update(request, *args, **kwargs)  # may throw validation errors
                wfrun_id = str(wfrun.uuid)
                registry.tasks['rodan.core.cancel_workflowrun'].apply_async((wfrun_id, ))
                return response
            elif old_status in (task_status.CANCELLED, task_status.FAILED) and new_status == task_status.RETRYING:
                response = self.partial_update(request, *args, **kwargs)  # may throw validation errors
                wfrun_id = str(wfrun.uuid)
                registry.tasks['rodan.core.retry_workflowrun'].apply_async((wfrun_id, ))
                return response
            elif new_status is not None:
                raise CustomAPIException({'status': ["Invalid status update"]}, status=status.HTTP_400_BAD_REQUEST)
            else:
                raise CustomAPIException({'status': ["Invalid status update"]}, status=status.HTTP_400_BAD_REQUEST)
        else:  # not updating status
            return self.partial_update(request, *args, **kwargs)
