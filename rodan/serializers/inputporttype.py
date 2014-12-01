from rest_framework import serializers
from rodan.models.inputporttype import InputPortType


class InputPortTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = InputPortType
        fields = ("url",
                  "uuid",
                  "job",
                  "name",
                  "minimum",
                  "maximum",
                  "resource_types")
