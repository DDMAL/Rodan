from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from django.core.urlresolvers import Resolver404
from django.contrib.auth.models import User
from rodan.helpers.object_resolving import resolve_to_object
from rodan.models.workflow import Workflow
from rodan.models.workflowjob import WorkflowJob
from rodan.models.resourceassignment import ResourceAssignment
from rodan.models.connection import Connection
from rodan.models.inputport import InputPort
from rodan.models.outputport import OutputPort
from rodan.models.inputporttype import InputPortType
from rodan.models.project import Project
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

        try:
            project_obj = resolve_to_object(project, Project)
        except Resolver404:
            return Response({'message': "Could not resolve Project ID to a Project"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except AttributeError:
            return Response({'message': "Please specify a project"}, status=status.HTTP_400_BAD_REQUEST)
        except Project.DoesNotExist:
            return Response({'message': "No project with specified uuid exists"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_obj = resolve_to_object(creator, User)
        except Resolver404:
            return Response({'message': "Could not resolve 'creator' to a User instance"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except AttributeError:
            user_obj = request.user
        except User.DoesNotExist:
            return Response({'message': "The specified user does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        if valid:
            return Response({'message': "You can't POST a valid workflow - it must be validated through a PATCH request"}, status=status.HTTP_200_OK)

        if not name:
            return Response({'message': "You must supply a name for your workflow"}, status=status.HTTP_400_BAD_REQUEST)

        workflow = Workflow(project=project_obj,
                            name=name,
                            valid=valid,
                            creator=user_obj)

        workflow.save()

        return Response(WorkflowSerializer(workflow).data, status=status.HTTP_201_CREATED)


class WorkflowDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Workflow

    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = WorkflowSerializer

    def patch(self, request, pk, *args, **kwargs):
        try:
            workflow = Workflow.objects.get(pk=pk)
        except Workflow.DoesNotExist:
            return Response({'message': 'Workflow not found'}, status=status.HTTP_404_NOT_FOUND)

        kwargs['partial'] = True
        to_be_validated = request.DATA.get('valid', None)
        workflow.valid = False
        workflow_jobs = WorkflowJob.objects.filter(workflow=workflow)
        resource_assignments = ResourceAssignment.objects.filter(workflow=workflow)

        if not to_be_validated:
            return self.update(request, *args, **kwargs)

        try:
            self._validate(workflow, workflow_jobs, resource_assignments)

        except NoWorkflowJobsError:
            return Response({'message': 'No WorkflowJobs in Workflow'}, status=status.HTTP_409_CONFLICT)

        except MultipleResourceCollectionsError:
            return Response({'message': 'Multiple resource assignment collections found'}, status=status.HTTP_409_CONFLICT)

        except ResourceNotInWorkflowError:
            return Response({'message': 'The resource {0} is not in the workflow'.format(ResourceNotInWorkflowError.name)}, status=status.HTTP_409_CONFLICT)

        except OrphanError:
            return Response({'message': 'The WorkflowJob with ID {0} is not connected to the rest of the workflow'.format(OrphanError.ID)}, status=status.HTTP_409_CONFLICT)

        except LoopError:
            return Response({'message': 'There appears to be a loop in the workflow'}, status=status.HTTP_409_CONFLICT)

        except NumberOfPortsError:
            return Response({'message': 'The number of input ports on WorkflowJob {0} did not meet the requirements'.format(NumberOfPortsError.ID)}, status=status.HTTP_409_CONFLICT)

        except NoOutputPortError:
            return Response({'message': 'The WorkflowJob {0} has no OutputPorts'.format(NoOutputPortError.ID)}, status=status.HTTP_409_CONFLICT)

        workflow.valid = True

        workflow.save()
        return self.partial_update(request, *args, **kwargs)

    def _validate(self, workflow,  workflow_jobs, resource_assignments):
        if not workflow_jobs:
            raise NoWorkflowJobsError

        start_points = []

        self._resource_assignment_validate(workflow, workflow_jobs, resource_assignments, start_points)

        self._find_remaining_start_points(workflow_jobs, start_points)

        self._detect_orphans(start_points)

        self._workflow_traversal(start_points)

    def _resource_assignment_validate(self, workflow, workflow_jobs, resource_assignments, start_points):
        multiple_resources_found = False

        for ra in resource_assignments:
            resource_list = ra.resources.all()

            if resource_list.count() > 1:
                if multiple_resources_found:
                    raise MultipleResourceCollectionsError

                multiple_resources_found = True

            for res in resource_list:
                if res not in workflow.resource_set.all():
                    ResourceNotInWorkflowError.name = res.name
                    raise ResourceNotInWorkflowError

            start_points.append(ra.input_port.workflow_job)

    def _find_remaining_start_points(self, workflow_jobs, start_points):
        for wfjob in workflow_jobs:
            inputs = InputPort.objects.filter(workflow_job=wfjob)

            if not inputs:
                start_points.append(wfjob)

    def _detect_orphans(self, start_points):
        for wfjob in start_points:
            outgoing_connections = Connection.objects.filter(output_workflow_job=wfjob)

            if len(start_points) > 1 and not outgoing_connections:
                OrphanError.ID = wfjob.uuid
                raise OrphanError

    def _workflow_traversal(self, start_points):
        total_visits = []

        for wfjob in start_points:
            start_point_visits = []

            self._workflow_valid(wfjob, start_point_visits, total_visits)

    def _workflow_valid(self, wfjob, start_point_visits, total_visits):
        start_point_visits.append(wfjob)

        self._workflow_job_visit(wfjob, total_visits)

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

            self._workflow_valid(wfj, start_point_visits, total_visits)

    def _workflow_job_visit(self, wfjob, total_visits):
        self._workflow_job_validate(wfjob)

        input_ports = InputPort.objects.filter(workflow_job=wfjob)

        for ip in input_ports:
            if Connection.objects.filter(input_port=ip):
                conn = Connection.objects.get(input_port=ip)
                total_visits.append(conn)

            elif ResourceAssignment.objects.filter(input_port=ip):
                ra = ResourceAssignment.objects.get(input_port=ip)
                total_visits.append(ra)

        total_visits.append(wfjob)

    def _workflow_job_validate(self, wfjob):
        output_ports = OutputPort.objects.filter(workflow_job=wfjob)

        if not output_ports:
            NoOutputPortError.ID = wfjob.uuid
            raise NoOutputPortError

        input_port_types = InputPortType.objects.filter(job=wfjob.job)

        for ipt in input_port_types:
            number_of_input_ports = InputPort.objects.filter(workflow_job=wfjob, input_port_type=ipt).count()

            if number_of_input_ports > ipt.maximum or number_of_input_ports < ipt.minimum:
                NumberOfPortsError.ID = wfjob.uuid
                raise NumberOfPortsError


class LoopError(Exception):
    pass


class NoOutputPortError(Exception):
    ID = ""


class NumberOfPortsError(Exception):
    ID = ""


class MultipleResourceCollectionsError(Exception):
    pass


class OrphanError(Exception):
    ID = ""


class NoWorkflowJobsError(Exception):
    pass


class ResourceNotInWorkflowError(Exception):
    name = ""
