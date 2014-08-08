from rest_framework import generics
from rest_framework import status
from rest_framework import permissions
from rest_framework.response import Response
from django.core.urlresolvers import Resolver404
from rodan.helpers.object_resolving import resolve_to_object
from rodan.models.connection import Connection
from rodan.models.inputport import InputPort
from rodan.models.outputport import OutputPort
from rodan.models.workflowjob import WorkflowJob
from rodan.serializers.connection import ConnectionListSerializer, ConnectionSerializer


class ConnectionList(generics.ListCreateAPIView):
    model = Connection
    serializer_class = ConnectionListSerializer
    permission_classes = (permissions.IsAuthenticated, )
    paginate_by = None

    def post(self, request, *args, **kwargs):
        input_port = request.DATA.get('input_port', None)
        input_workflow_job = request.DATA.get('input_workflow_job', None)
        output_port = request.DATA.get('output_port', None)
        output_workflow_job = request.DATA.get('output_workflow_job', None)

        try:
            ip_obj = resolve_to_object(input_port, InputPort)
        except AttributeError:
            return Response({'message': "Please specify an input port"}, status=status.HTTP_400_BAD_REQUEST)
        except Resolver404:
            return Response({'message': "Problem resolving input port object"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except InputPort.DoesNotExist:
            return Response({'message': "No input port with the specified uuid exists"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            op_obj = resolve_to_object(output_port, OutputPort)
        except AttributeError:
            return Response({'message': "Please specify an output port"}, status=status.HTTP_400_BAD_REQUEST)
        except Resolver404:
            return Response({'message': "Problem resolving output port object"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except OutputPort.DoesNotExist:
            return Response({'message': "No output port with the specified uuid exists"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            injob_obj = resolve_to_object(input_workflow_job, WorkflowJob)
        except AttributeError:
            return Response({'message': "Please specify an input workflowjob"}, status=status.HTTP_400_BAD_REQUEST)
        except Resolver404:
            return Response({'message': "Problem resolving the input workflowjob"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except WorkflowJob.DoesNotExist:
            return Response({'message': "No workflowjob with the specified uuid exists"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            outjob_obj = resolve_to_object(output_workflow_job, WorkflowJob)
        except AttributeError:
            return Response({'message': "Please specify an output workflowjob"}, status=status.HTTP_400_BAD_REQUEST)
        except Resolver404:
            return Response({'message': "Problem resolving the output workflowjob"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except WorkflowJob.DoesNotExist:
            return Response({'message': "No workflowjob with the specified uuid exists"}, status=status.HTTP_400_BAD_REQUEST)

        if outjob_obj.workflow != injob_obj.workflow:
            return Response({"message": "Input and output WorkflowJobs must be part of the same workflow"}, status.HTTP_200_OK)

        connection = Connection(input_port=ip_obj,
                                input_workflow_job=injob_obj,
                                output_port=op_obj,
                                output_workflow_job=outjob_obj)
        connection.save()

        return Response({"connection": ConnectionSerializer(connection).data}, status=status.HTTP_201_CREATED)


class ConnectionDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Connection
    serializer_class = ConnectionSerializer
    permission_classes = (permissions.IsAuthenticated, )
