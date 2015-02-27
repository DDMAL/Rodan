import jsonschema
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from rodan.paginators.pagination import PaginationSerializer
from rodan.models import Workflow, InputPort, OutputPort
from rodan.serializers.workflow import WorkflowSerializer, WorkflowListSerializer, version_map
from rodan.exceptions import CustomAPIException
from django.conf import settings


class WorkflowList(generics.ListCreateAPIView):
    """
    Returns a list of all Workflows. Accepts a POST request with a data body to
    create a new Workflow. POST requests will return the newly-created Workflow object.

    #### Parameters
    - `project` -- GET & POST. UUID of a Project for GET, URL of a Project for POST.
    - `name` -- POST-only.
    - `valid` -- (optional) POST-only. Should be empty string.
    """
    model = Workflow
    # permission_classes = (permissions.IsAuthenticated, )
    permission_classes = (permissions.AllowAny, )
    serializer_class = WorkflowListSerializer
    pagination_serializer_class = PaginationSerializer
    filter_fields = ('project', )
    queryset = Workflow.objects.all() # [TODO] filter according to the user?

    def perform_create(self, serializer):
        valid = serializer.validated_data.get('valid', False)
        if valid:
            raise ValidationError({'valid': ["You can't create a valid workflow - it must be validated through a PATCH request."]})

        serializer.save(creator=self.request.user)


class WorkflowDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Performs operations on a single Workflow instance.

    #### Parameters
    - `export` -- GET-only. If provided, Rodan will export the workflow into JSON format.
    - `valid` -- PATCH-only. If provided with non-empty string, workflow validation
      will be triggered.
    """
    model = Workflow
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = WorkflowSerializer
    queryset = Workflow.objects.all() # [TODO] filter according to the user?

    def get(self, request, *a, **k):
        if 'export' in request.query_params:
            wf = self.get_object()
            serialized = version_map[settings.RODAN_WORKFLOW_SERIALIZATION_FORMAT_VERSION].dump(wf)
            return Response(serialized)
        else:
            return super(WorkflowDetail, self).get(request, *a, **k)

    def perform_update(self, serializer):
        if 'valid' in serializer.validated_data:
            to_be_validated = serializer.validated_data.get('valid', False)
            if to_be_validated:
                workflow = self.get_object()

                try:
                    self._validate(workflow)
                except WorkflowValidationError as e:
                    raise CustomAPIException(e.message, status=status.HTTP_409_CONFLICT)
            else:
                raise ValidationError({"valid": "Cannot invalidate a Workflow."})

        serializer.save()

    def _validate(self, workflow):
        # validate WorkflowJobs
        workflow_jobs = workflow.workflow_jobs.all()
        for wfjob in workflow_jobs:
            number_of_output_ports = wfjob.output_ports.count()
            if number_of_output_ports == 0:
                raise WorkflowValidationError('The WorkflowJob {0} has no OutputPorts'.format(wfjob.uuid))

            job = wfjob.job
            input_port_types = job.input_port_types.all()
            output_port_types = job.output_port_types.all()

            for ipt in input_port_types:
                number_of_input_ports = wfjob.input_ports.filter(input_port_type=ipt).count()
                if number_of_input_ports > ipt.maximum or number_of_input_ports < ipt.minimum:
                    raise WorkflowValidationError('The number of input ports on WorkflowJob {0} did not meet the requirements'.format(wfjob.uuid))

            for opt in output_port_types:
                number_of_output_ports = wfjob.output_ports.filter(output_port_type=opt).count()
                if number_of_output_ports > opt.maximum or number_of_output_ports < opt.minimum:
                    raise WorkflowValidationError('The number of output ports on WorkflowJob {0} did not meet the requirements'.format(wfjob.uuid))

            v = jsonschema.Draft4Validator(dict(job.settings))  # convert JSONDict object to Python dict object.
            try:
                v.validate(wfjob.job_settings)
            except jsonschema.exceptions.ValidationError as e:
                raise WorkflowValidationError('WorkflowJob {0} has invalid settings.'.format(wfjob.uuid))

        # validate InputPorts
        input_ports = InputPort.objects.filter(workflow_job__workflow=workflow)
        for ip in input_ports:
            if ip.input_port_type.job != ip.workflow_job.job:
                raise WorkflowValidationError('InputPort {0} has an InputPortType incompatible with its WorkflowJob'.format(ip.uuid))

            if ip.connections.count() > 1:
                raise WorkflowValidationError('InputPort {0} has multiple Connections'.format(ip.uuid))

        # validate OutputPorts
        output_ports = OutputPort.objects.filter(workflow_job__workflow=workflow)
        for op in output_ports:
            if op.output_port_type.job != op.workflow_job.job:
                raise WorkflowValidationError('OutputPort {0} has an OutputPortType incompatible with its WorkflowJob'.format(op.uuid))
            resource_type_set = set(op.output_port_type.resource_types.all())
            for connection in op.connections.all():
                ip = connection.input_port
                in_type_set = set(ip.input_port_type.resource_types.all())
                resource_type_set = resource_type_set.intersection(in_type_set)
                if not set(resource_type_set):
                    raise WorkflowValidationError('There is no common resource type between OutputPort {0} and its connected InputPorts'.format(op.uuid))

        # graph validation
        ## Step 0
        if len(workflow_jobs) == 0:
            raise WorkflowValidationError('No WorkflowJobs in Workflow')

        ## Step 1
        self.visited_set_global = set()

        ## Step 2
        self.disjoint_set = DisjointSet(workflow_jobs)

        ## Step 3&4
        for wfjob in workflow_jobs:
            try:
                self._integrated_depth_first_search(wfjob)
            except WorkflowValidationError as e:
                raise e

        ## Step 5
        one_set = self.disjoint_set.find(workflow_jobs[0])
        for wfjob in workflow_jobs:
            if self.disjoint_set.find(wfjob) is not one_set:
                raise WorkflowValidationError('Workflow is not connected')

        # Valid!
        return True

    def _integrated_depth_first_search(self, this_wfjob):
        if this_wfjob in self.visited_set_global:
            return
        self.visited_set_global.add(this_wfjob)

        for op in this_wfjob.output_ports.all():
            adjacent_wfjobs = set()
            connections = op.connections.all()
            for conn in connections:
                adj_wfjob = conn.input_port.workflow_job
                if adj_wfjob not in adjacent_wfjobs:
                    self._integrated_depth_first_search(adj_wfjob)
                    if self.disjoint_set.find(this_wfjob) is self.disjoint_set.find(adj_wfjob):
                        raise WorkflowValidationError('There appears to be a loop in the workflow')
                    adjacent_wfjobs.add(adj_wfjob)

            for adj_wfjob in adjacent_wfjobs:
                self.disjoint_set.union(this_wfjob, adj_wfjob)



class WorkflowValidationError(Exception):
    message = None

    def __init__(self, message):
        super(WorkflowValidationError, self).__init__()
        self.message = message


class DisjointSet(object):
    def __init__(self, xs):
        self._parent = {}
        # MakeSet
        for x in xs:
            self._parent[x] = x

    def find(self, x):
        parent = self._parent[x]
        if parent is x:
            return x
        else:
            new_parent = self.find(parent)
            self._parent[x] = new_parent
            return new_parent

    def union(self, x, y):
        x_root = self.find(x)
        y_root = self.find(y)
        self._parent[x_root] = y_root
