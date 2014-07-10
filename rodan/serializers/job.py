from rest_framework import serializers
from rodan.models.job import Job


class JobSerializer(serializers.HyperlinkedModelSerializer):
    settings = serializers.CharField(required=False)  # this actually sends it as JSON

    input_port_types = serializers.Field(source="input_port_types")
    output_port_types = serializers.Field(source="output_port_types")

    class Meta:
        model = Job
        fields = ("url",
                  "job_name",
                  "settings",
                  "input_port_types",
                  "output_port_types",
                  "description",
                  "category",
                  'enabled',
                  'interactive')
