import urlparse
from django.core.urlresolvers import resolve

from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response

from rodan.models.workflow import Workflow
from rodan.models.workflowjob import WorkflowJob
from rodan.models.resourceassignment import ResourceAssignment
from rodan.models.connection import Connection
from rodan.models.inputport import InputPort
from rodan.models.outputport import OutputPort
from rodan.models.inputporttype import InputPortType
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
        creator = request.DATA.get('creator', None)
        workflow_jobs = request.DATA.get('workfow_jobs', None)

        if valid:
            return Response({'message': "You can't POST a valid workflow - it must be validated through a PATCH request"}, status=status.HTTP_400_BAD_REQUEST)

        workflow = Workflow(project=project, name=name, valid=valid, creator=creator, workflow_jobs=workflow_jobs)
        workflow.save()

        return Response(status=status.HTTP_201_CREATED)


class WorkflowDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Workflow

    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = WorkflowSerializer

    def patch(self, request, pk, *args, **kwargs):
        kwargs['partial'] = True
        workflow = Workflow.objects.get(pk=pk)
        to_be_validated = request.DATA.get('valid', None)
        workflow.valid = False
        workflow_jobs = WorkflowJob.objects.filter(workflow=workflow)
        resource_assignments = ResourceAssignment.objects.filter(workflow=workflow)

        if not workflow:
            return Response({'message': "Workflow not found"}, status=status.HTTP_404_NOT_FOUND)

        if not to_be_validated:
            return self.update(request, *args, **kwargs)

        if not workflow_jobs:
            return Response({'message': 'No WorkflowJobs in Workflow'}, status=status.HTTP_400_BAD_REQUEST)

        multiple_resources_found = False
        start_points = []

        for ra in resource_assignments:
            resource_list = ra.resources.all()

            if resource_list.count() > 1:
                if multiple_resources_found:
                    return Response({'message': 'Multiple resource assignment collections found'}, status=status.HTTP_400_BAD_REQUEST)

                multiple_resources_found = True

            for res in resource_list:
                if res not in workflow.resource_set.all():
                    return Response({'message': 'The resource {0} is not in the workflow'.format(res.name)}, status=status.HTTP_400_BAD_REQUEST)

            start_points.append(ra.input_port.workflow_job)

        for wfjob in workflow_jobs:
            inputs = InputPort.objects.filter(workflow_job=wfjob)

            if not inputs:
                start_points.append(wfjob)

        total_visits = []
        for wfjob in start_points:
            start_point_visits = []

            try:
                self.workflow_valid(wfjob, start_point_visits, total_visits)

            except LoopError:
                return Response({'message': 'There appears to be a loop in the workflow'}, status=status.HTTP_400_BAD_REQUEST)

            except NumberOfPortsError:
                return Response({'message': 'The number of input ports on WorkflowJob {0} did not meet the requriements'.format(NumberOfPortsError.ID)}, status=status.HTTP_400_BAD_REQUEST)

            except NoOutputPortError:
                return Response({'message': 'The WorkflowJob {0} has no OutputPorts!'.format(NoOutputPortError.ID)}, status=status.HTTP_400_BAD_REQUEST)

        workflow.valid = True
        workflow.save()

        for wjfob in workflow_jobs:
            if wfjob not in total_visits:
                return Response({'message': 'The WorkflowJob with ID {0} was not visited'.format(wfjob.uuid)}, status=status.HTTP_400_BAD_REQUEST)

        return self.update(request, *args, **kwargs)

    def workflow_job_valid(self, wfjob):
        output_ports = OutputPort.objects.filter(workflow_job=wfjob)

        if not output_ports:
            NoOutputPortError.ID = wfjob.uuid
            raise NoOutputPortError

        input_port_types = InputPortType.objects.filter(job=wfjob.job)

        for ipt in input_port_types:
            number_of_input_ports = InputPort.objects.filter(input_port_type=ipt).count()

            if number_of_input_ports > ipt.maximum or number_of_input_ports < ipt.minimum:
                NumberOfPortsError.ID = wfjob.uuid
                raise NumberOfPortsError

    def workflow_job_visit(self, wfjob, total_visits):
        try:
            self.workflow_job_valid(wfjob)
        except Exception as e:
            raise e

        input_ports = InputPort.objects.filter(workflow_job=wfjob)

        for ip in input_ports:
            if Connection.objects.filter(input_port=ip):
                conn = Connection.objects.get(input_port=ip)

                if conn in total_visits:
                    return

                total_visits.append(conn)

            elif ResourceAssignment.objects.filter(input_port=ip):
                ra = ResourceAssignment.objects.get(input_port=ip)

                if ra in total_visits:
                    return

                total_visits.append(ra)

        total_visits.append(wfjob)

    def workflow_valid(self, wfjob, start_point_visits, total_visits):
        start_point_visits.append(wfjob)

        try:
            self.workflow_job_visit(wfjob, total_visits)

        except Exception as e:
            raise e

        adjacent_connections = Connection.objects.filter(output_workflow_job=wfjob)

        for conn in adjacent_connections:
            if conn in start_point_visits:
                return

            start_point_visits.append(conn)
            wfj = conn.input_workflow_job

            if wfj in start_point_visits:
                raise LoopError

            if wfj in total_visits:
                return

            self.workflow_valid(wfj, start_point_visits, total_visits)


class LoopError(Exception):
    pass


class NoOutputPortError(Exception):
    ID = ""
    pass


class NumberOfPortsError(Exception):
    ID = ""
    pass
