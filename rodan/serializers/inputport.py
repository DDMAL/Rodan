from rest_framework import serializers
from rodan.models.inputport import InputPort


class InputPortSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = InputPort
        fields = ("url",
                  "input_port_type",
                  "label",
                  "workflow_job")
