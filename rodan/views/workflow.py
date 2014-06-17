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
        connections = Connection.objects.filter(workflow=workflow)

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

        # for wfjob in workflow_jobs:
        #     if not wfjob.input_port_set and wfjob not in start_points:
        #         start_points.append(wfjob)
        for wfjob in start_points:
            start_point_visits = []
            try:
                self.DFS(wfjob, start_point_visits)
            except LoopError:
                return Response({'message': 'There appears to be a loop in the workflow'}, status=status.HTTP_400_BAD_REQUEST)

        workflow.valid = True
        workflow.save()

        return self.update(request, *args, **kwargs)

    def DFS(self, wfjob, start_point_visits):
        start_point_visits.append(wfjob)
        adjacent_connections = Connection.objects.filter(output_workflow_job=wfjob)
        for conn in adjacent_connections:
            if conn not in start_point_visits:
                start_point_visits.append(conn)
                wfj = conn.input_workflow_job
                if wfj in start_point_visits:
                    raise LoopError
                    # node_visit(wfj)
                self.DFS(wfj, start_point_visits)


class LoopError(Exception):
    pass
