from rest_framework import generics
from rest_framework import status
from rest_framework import permissions
from rest_framework.response import Response
from django.core.urlresolvers import Resolver404
from rodan.helpers.object_resolving import resolve_to_object
from rodan.models.resourceassignment import ResourceAssignment
from rodan.models.inputport import InputPort
from rodan.models.workflow import Workflow
from rodan.models.workflowjob import WorkflowJob
from rodan.serializers.resourceassignment import ResourceAssignmentSerializer


class ResourceAssignmentList(generics.ListCreateAPIView):
    model = ResourceAssignment
    serializer_class = ResourceAssignmentSerializer
    permission_classes = (permissions.IsAuthenticated, )
    paginate_by = None

    def post(self, request, *args, **kwargs):
        input_port = request.DATA.get('input_port', None)
        try:
            ip_obj = resolve_to_object(input_port, InputPort)
        except Resolver404:
            return Response({'message': "Couldn't resolve InputPort object"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except AttributeError:
            return Response({'message': "Please specify an input port"}, status=status.HTTP_400_BAD_REQUEST)
        except InputPort.DoesNotExist:
            return Response({'message': "No input port with specified uuid exists"}, status=status.HTTP_400_BAD_REQUEST)

        workflow = request.DATA.get('workflow', None)
        try:
            wf_obj = resolve_to_object(workflow, Workflow)
        except Resolver404:
            return Response({'message': "Couldn't resolve Workflow object"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except AttributeError:
            return Response({'message': "Please sepcify a workflow"}, status=status.HTTP_400_BAD_REQUEST)
        except Workflow.DoesNotExist:
            return Response({'message': "No workflow with specified uuid exists"}, status=status.HTTP_400_BAD_REQUEST)

        workflow_job = request.DATA.get('workflow_job', None)
        try:
            wfj_obj = resolve_to_object(workflow_job, WorkflowJob)
        except Resolver404:
            return Response({'message': "Could't resolve WorkflowJob object"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except AttributeError:
            return Response({'message': "Please specify a workflowjob"}, status=status.HTTP_400_BAD_REQUEST)
        except WorkflowJob.DoesNotExist:
            return Response({'message': "No workflowjob with specified uuid exists"}, status.HTTP_400_BAD_REQUEST)
        resource_assignment = ResourceAssignment(input_port=ip_obj,
                                                 workflow=wf_obj,
                                                 workflow_job=wfj_obj)
        resource_assignment.save()

        return Response(ResourceAssignmentSerializer(resource_assignment).data, status=status.HTTP_201_CREATED)


class ResourceAssignmentDetail(generics.RetrieveUpdateDestroyAPIView):
    model = ResourceAssignment
    serializer_class = ResourceAssignmentSerializer
    permission_classes = (permissions.IsAuthenticated, )
