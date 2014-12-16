from rest_framework import serializers
from rodan.models.connection import Connection
from rodan.serializers.inputport import InputPortSerializer
from rodan.serializers.workflowjob import WorkflowJobSerializer
from rodan.serializers.outputport import OutputPortSerializer
from rodan.serializers.workflow import WorkflowSerializer


class ConnectionSerializer(serializers.HyperlinkedModelSerializer):
    input_workflow_job = WorkflowJobSerializer(read_only=True)
    output_workflow_job = WorkflowJobSerializer(read_only=True)
    workflow = WorkflowSerializer(read_only=True)

    class Meta:
        model = Connection
        fields = ("url",
                  "uuid",
                  "input_port",
                  "input_workflow_job",
                  "output_port",
                  "output_workflow_job",
                  "workflow")

    def validate(self, data):
        if self.partial:
            ip = data.get('input_port', self.instance.input_port)
            op = data.get('output_port', self.instance.output_port)
        else:
            ip = data['input_port']
            op = data['output_port']

        if ip.workflow_job.workflow != op.workflow_job.workflow:
            raise serializers.ValidationError("The InputPort is not in the same workflow as the OutputPort.")

        return data
