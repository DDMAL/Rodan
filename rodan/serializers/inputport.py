from rest_framework import serializers
from rodan.models.inputport import InputPort


class InputPortSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = InputPort
        read_only_fields = ("resource_assignments", "connections")
        fields = ("url",
                  "uuid",
                  "input_port_type",
                  "label",
                  "workflow_job",
                  "resource_assignments",
                  "connections",)
