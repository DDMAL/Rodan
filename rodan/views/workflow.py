from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from django.core.urlresolvers import Resolver404
from django.contrib.auth.models import User
from rodan.helpers.object_resolving import resolve_to_object
from rodan.models import Workflow, WorkflowJob, ResourceAssignment, Connection, InputPort, OutputPort, InputPortType, OutputPortType, Project
from rodan.serializers.user import UserSerializer
from rodan.serializers.workflow import WorkflowSerializer, WorkflowListSerializer


class WorkflowList(generics.ListCreateAPIView):
    model = Workflow
    # permission_classes = (permissions.IsAuthenticated, )
    permission_classes = (permissions.AllowAny, )
    serializer_class = WorkflowListSerializer
    paginate_by = None

    def get_queryset(self):
        queryset = Workflow.objects.all()
        project = self.request.QUERY_PARAMS.get('project', None)

        if project:
            queryset = queryset.filter(project__uuid=project)

        return queryset

    def post(self, request, *args, **kwargs):
        kwargs['partial'] = True
        project = request.DATA.get('project', None)
        name = request.DATA.get('name', None)
        valid = request.DATA.get('valid', None)

        user_obj = UserSerializer(request.user).data
        request.DATA['creator'] = user_obj['url']

        try:
            resolve_to_object(project, Project)
        except Resolver404:
            return Response({'message': "Could not resolve Project ID to a Project"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except AttributeError:
            return Response({'message': "Please specify a project"}, status=status.HTTP_400_BAD_REQUEST)
        except Project.DoesNotExist:
            return Response({'message': "No project with specified uuid exists"}, status=status.HTTP_400_BAD_REQUEST)

        if valid:
            return Response({'message': "You can't POST a valid workflow - it must be validated through a PATCH request"}, status=status.HTTP_200_OK)

        if not name:
            return Response({'message': "You must supply a name for your workflow"}, status=status.HTTP_400_BAD_REQUEST)

        return self.create(request, *args, **kwargs)


class WorkflowDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Workflow

    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = WorkflowSerializer

    def patch(self, request, pk, *args, **kwargs):
        try:
            workflow = Workflow.objects.get(pk=pk)
        except Workflow.DoesNotExist:
            return Response({'message': 'Workflow not found'}, status=status.HTTP_404_NOT_FOUND)

        #kwargs['partial'] = True
        to_be_validated = request.DATA.get('valid', None)
        #workflow.valid = False

        resource_assignments = ResourceAssignment.objects.filter(input_port__workflow_job__workflow=workflow)

        if not to_be_validated:
            return super(WorkflowDetail, self).patch(request, *args, **kwargs)

        try:
            self._validate(workflow)
        except WorkflowValidationError as e:
            return e.response

        #workflow.valid = True
        #workflow.save()

        return super(WorkflowDetail, self).patch(request, *args, **kwargs)


    def _validate(self, workflow):
        # validate WorkflowJobs
        workflow_jobs = workflow.workflow_jobs.all()
        for wfjob in workflow_jobs:
            number_of_output_ports = wfjob.output_ports.count()
            if number_of_output_ports == 0:
                raise WorkflowValidationError(response=Response({'message': 'The WorkflowJob {0} has no OutputPorts'.format(wfjob.uuid)}, status=status.HTTP_409_CONFLICT))

            job = wfjob.job
            input_port_types = job.input_port_types.all()
            output_port_types = job.output_port_types.all()

            for ipt in input_port_types:
                number_of_input_ports = wfjob.input_ports.filter(input_port_type=ipt).count()
                if number_of_input_ports > ipt.maximum or number_of_input_ports < ipt.minimum:
                    raise WorkflowValidationError(response=Response({'message': 'The number of input ports on WorkflowJob {0} did not meet the requirements'.format(wfjob.uuid)}, status=status.HTTP_409_CONFLICT))

            for opt in output_port_types:
                number_of_output_ports = wfjob.output_ports.filter(output_port_type=opt).count()
                if number_of_output_ports > opt.maximum or number_of_output_ports < opt.minimum:
                    raise WorkflowValidationError(response=Response({'message': 'The number of output ports on WorkflowJob {0} did not meet the requirements'.format(wfjob.uuid)}, status=status.HTTP_409_CONFLICT))

            # [TODO] check settings argtype

        # validate InputPorts
        input_ports = InputPort.objects.filter(workflow_job__workflow=workflow)
        for ip in input_ports:
            number_of_connection = ip.connections.count()
            number_of_resource_assignment = ip.resource_assignments.count()
            if number_of_connection + number_of_resource_assignment > 1:
                raise WorkflowValidationError(response=Response({'message': 'InputPort {0} has more than one Connection or ResourceAssignment'.format(ip.uuid)}, status=status.HTTP_409_CONFLICT))

        # OutputPorts do not need validation

        # validate Connections
        connections = Connection.objects.filter(input_port__workflow_job__workflow=workflow, output_port__workflow_job__workflow=workflow)
        for connection in connections:
            op = connection.output_port
            out_type = op.output_port_type.resource_type
            ip = connection.input_port
            in_type = ip.input_port_type.resource_type

            if not resource_type_of_connection_agreed(out_type, in_type):
                raise WorkflowValidationError(response=Response({'message': 'The resource type of OutputPort {0} does not agree with connected InputPort {1}'.format(op.uuid, ip.uuid)}, status=status.HTTP_409_CONFLICT))

        # validate ResourceAssignments
        resource_assignments = ResourceAssignment.objects.filter(input_port__workflow_job__workflow=workflow)
        multiple_resources_found = False
        for ra in resource_assignments:
            number_of_resources = ra.resources.count()
            if number_of_resources > 1:
                if multiple_resources_found:
                    raise WorkflowValidationError(response=Response({'message': 'Multiple resource assignment collections found'}, status=status.HTTP_409_CONFLICT))
                multiple_resources_found = True
            elif number_of_resources == 0:
                raise WorkflowValidationError(response=Response({'message': 'No resource assigned by ResourceAssignment {0}'.format(ra.uuid)}, status=status.HTTP_409_CONFLICT))

            ip = ra.input_port
            type_of_ip = ip.input_port_type.resource_type
            resources = ra.resources.all()
            for res in resources:
                if res.project.uuid != ra.input_port.workflow_job.workflow.project.uuid:
                    raise WorkflowValidationError(response=Response({'message': 'The resource {0} is not in the project'.format(res.name)}, status=status.HTTP_409_CONFLICT))
                if not res.processed:
                    raise WorkflowValidationError(response=Response({'message': 'The resource {0} has not been processed'.format(res.name)}, status=status.HTTP_409_CONFLICT))
                if not resource_type_of_resource_assignment_agreed(res.resource_type, type_of_ip):  # TODO
                    raise WorkflowValidationError(response=Response({'message': 'The type of resource {0} assigned does not agree with InputPort {1}'.format(res.name, ip.uuid)}, status=status.HTTP_409_CONFLICT))

        # graph validation
        ## Step 0
        if len(workflow_jobs) == 0:
            raise WorkflowValidationError(response=Response({'message': 'No WorkflowJobs in Workflow'}, status=status.HTTP_409_CONFLICT))

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
                raise WorkflowValidationError(response=Response({'message': 'Workflow is not connected'}, status=status.HTTP_409_CONFLICT))

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
                    if self.disjoint_set.find(this_wfjob) is self.disjoint_set.find(adj_wfjob):
                        raise WorkflowValidationError(response=Response({'message': 'There appears to be a loop in the workflow'}, status=status.HTTP_409_CONFLICT))
                    self.disjoint_set.union(this_wfjob, adj_wfjob)
                    self._integrated_depth_first_search(adj_wfjob)
                    adjacent_wfjobs.add(adj_wfjob)


class WorkflowValidationError(Exception):
    response = None

    def __init__(self, response):
        super(WorkflowValidationError, self).__init__()
        self.response = response


def resource_type_of_connection_agreed(typeA, typeB):
    # [TODO] move this function to a specific module like `RodanType.py`?
    return set(typeA).intersection(set(typeB))

def resource_type_of_resource_assignment_agreed(type_res, type_port):
    # [TODO] move this function to a specific module like `RodanType.py`?
    return True  # [TODO]

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
        xRoot = self.find(x)
        yRoot = self.find(y)
        self._parent[xRoot] = yRoot
