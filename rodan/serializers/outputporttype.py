from rest_framework import serializers
from rodan.models.outputporttype import OutputPortType


class OutputPortTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OutputPortType
        fields = ("url",
                  "uuid",
                  "job",
                  "name",
                  "minimum",
                  "maximum",
                  "is_list",
                  "resource_types")
