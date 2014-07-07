import urlparse
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.core.urlresolvers import resolve
from rodan.models.connection import Connection
from rodan.models.inputport import InputPort
from rodan.models.outputport import OutputPort
from rodan.models.workflowjob import WorkflowJob
from rodan.serializers.connection import ConnectionSerializer


class ConnectionList(generics.ListCreateAPIView):
    model = Connection
    serializer_class = ConnectionSerializer

    def post(self, request, *args, **kwargs):
        input_port = request.DATA.get('input_port', None)
        input_workflow_job = request.DATA.get('input_workflow_job', None)
        output_port = request.DATA.get('output_port', None)
        output_workflow_job = request.DATA.get('output_workflow_job', None)

        ip_obj = self._resolve_to_object(input_port, InputPort)
        op_obj = self._resolve_to_object(output_port, OutputPort)
        injob_obj = self._resolve_to_object(input_workflow_job, WorkflowJob)
        outjob_obj = self._resolve_to_object(output_workflow_job, WorkflowJob)

        if outjob_obj.workflow != injob_obj.workflow:
            return Response({"message": "Input and output WorkflowJobs must be part of the same workflow"}, status.HTTP_200_OK)

        connection = Connection(input_port=ip_obj,
                                input_workflow_job=injob_obj,
                                output_port=op_obj,
                                output_workflow_job=outjob_obj)
        connection.save()

        return Response({"uuid": connection.uuid.hex}, status=status.HTTP_201_CREATED)

    def _resolve_to_object(self, request_url, model):
        value = urlparse.urlparse(request_url).path
        o = resolve(value)
        obj_pk = o.kwargs.get('pk')
        return model.objects.get(pk=obj_pk)


class ConnectionDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Connection
    serializer_class = ConnectionSerializer
