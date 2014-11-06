from rest_framework import serializers
from rodan.models.outputport import OutputPort


class OutputPortSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OutputPort
        read_only_fields = ("connections",)
        fields = ("url",
                  "uuid",
                  "output_port_type",
                  "label",
                  "workflow_job",
                  "connections")
