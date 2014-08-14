from rest_framework import serializers
from rodan.models.resourceassignment import ResourceAssignment
from rodan.serializers.inputport import InputPortSerializer


class ResourceAssignmentSerializer(serializers.HyperlinkedModelSerializer):
    input_port = InputPortSerializer()

    class Meta:
        model = ResourceAssignment
        fields = ("url",
                  "uuid",
                  "input_port",
                  "resources",
                  "workflow",
                  "workflow_job")
