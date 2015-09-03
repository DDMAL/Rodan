from rest_framework import serializers
from rodan.models.inputport import InputPort


class InputPortSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = InputPort
        read_only_fields = ("connections", "extern")
        fields = ("url",
                  "uuid",
                  "input_port_type",
                  "label",
                  "extern",
                  "workflow_job",
                  "connections",)
