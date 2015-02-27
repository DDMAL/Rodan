from rest_framework import serializers
from rodan.models.inputport import InputPort


class InputPortSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = InputPort
        read_only_fields = ("connections", )
        fields = ("url",
                  "uuid",
                  "input_port_type",
                  "label",
                  "workflow_job",
                  "connections",)
