from rest_framework import serializers
from rodan.models.job import Job
from rodan.models.inputporttype import InputPortType
from rodan.models.outputporttype import OutputPortType
from rodan.serializers.inputporttype import InputPortTypeSerializer
from rodan.serializers.outputporttype import OutputPortTypeSerializer


class JobSerializer(serializers.HyperlinkedModelSerializer):
    settings = serializers.CharField(required=False)  # this actually sends it as JSON
    input_port_types = InputPortTypeSerializer(many=True)
    output_port_types = OutputPortTypeSerializer(many=True)

    class Meta:
        model = Job
        fields = ("url",
                  "uuid",
                  "job_name",
                  "settings",
                  "description",
                  "input_port_types",
                  "output_port_types",
                  "category",
                  'enabled',
                  'interactive')
