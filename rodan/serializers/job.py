from rest_framework import serializers
from rodan.models.job import Job
from rodan.models.inputporttype import InputPortType
from rodan.models.outputporttype import OutputPortType
from rodan.serializers.inputporttype import InputPortTypeSerializer
from rodan.serializers.outputporttype import OutputPortTypeSerializer


class JobSerializer(serializers.HyperlinkedModelSerializer):
    settings = serializers.CharField(required=False)  # this actually sends it as JSON

    input_port_types = serializers.SerializerMethodField("get_input_port_types")
    output_port_types = serializers.SerializerMethodField("get_output_port_types")

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

    def get_input_port_types(self, obj):
        return [InputPortTypeSerializer(ipt).data for ipt in InputPortType.objects.filter(job=obj)]

    def get_output_port_types(self, obj):
        return [OutputPortTypeSerializer(opt).data for opt in OutputPortType.objects.filter(job=obj)]
