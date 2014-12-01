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


class ConnectionListSerializer(serializers.HyperlinkedModelSerializer):
    input_workflow_job = serializers.HyperlinkedRelatedField(view_name="workflowjob-detail", read_only=True)
    output_workflow_job = serializers.HyperlinkedRelatedField(view_name="workflowjob-detail", read_only=True)
    workflow = serializers.HyperlinkedRelatedField(view_name="workflow-detail", read_only=True)

    class Meta:
        model = Connection
        fields = ("url",
                  "uuid",
                  "input_port",
                  "input_workflow_job",
                  "output_port",
                  "output_workflow_job",
                  "workflow")
