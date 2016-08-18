from rest_framework import serializers
from rodan.models.job import Job
from rodan.serializers.inputporttype import InputPortTypeSerializer
from rodan.serializers.outputporttype import OutputPortTypeSerializer
from rodan.serializers import TransparentField


class JobSerializer(serializers.HyperlinkedModelSerializer):
    settings = TransparentField(required=False)
    input_port_types = InputPortTypeSerializer(many=True)
    output_port_types = OutputPortTypeSerializer(many=True)

    class Meta:
        model = Job
        fields = ("url",
                  "uuid",
                  "name",
                  "settings",
                  "description",
                  "input_port_types",
                  "output_port_types",
                  "category",
                  'enabled',
                  'interactive')
