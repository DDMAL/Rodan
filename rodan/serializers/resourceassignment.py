from rest_framework import serializers
from rodan.models.resourceassignment import ResourceAssignment
from rodan.serializers.inputport import InputPortSerializer


class ResourceAssignmentSerializer(serializers.HyperlinkedModelSerializer):
    workflow = serializers.HyperlinkedRelatedField(view_name='workflow-detail', read_only=True)
    workflow_job = serializers.HyperlinkedRelatedField(view_name='workflowjob-detail', read_only=True)

    class Meta:
        model = ResourceAssignment
        fields = ("url",
                  "uuid",
                  "input_port",
                  "resources",
                  "workflow",
                  "workflow_job")
