from rest_framework import generics
from rest_framework import status
from rest_framework import permissions
from rest_framework.response import Response
from django.core.urlresolvers import Resolver404
from rodan.helpers.object_resolving import resolve_to_object
from rodan.models.connection import Connection
from rodan.models.inputport import InputPort
from rodan.models.outputport import OutputPort
from rodan.serializers.workflowjob import WorkflowJobSerializer
from rodan.serializers.connection import ConnectionListSerializer, ConnectionSerializer


class ConnectionList(generics.ListCreateAPIView):
    """
    Returns a list of Connections. Accepts a POST request with a data body to create
    a new Connection. POST requests will return the newly-created Connection object.

    #### Parameters
    - input_port -- POST-only, URL to an InputPort object
    - output_port -- POST-only, URL to an OutputPort object
    """
    model = Connection
    serializer_class = ConnectionListSerializer
    permission_classes = (permissions.IsAuthenticated, )
    paginate_by = None

    def post(self, request, *args, **kwargs):
        input_port = request.DATA.get('input_port', None)
        output_port = request.DATA.get('output_port', None)

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

        return self.create(request, *args, **kwargs)


class ConnectionDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Perform operations on a single Connection instance.
    """
    model = Connection
    serializer_class = ConnectionSerializer
    permission_classes = (permissions.IsAuthenticated, )
