from rest_framework import serializers
from rodan.models.job import Job

class JobSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Job
        fields = ("url",
                  "name",
                  "arguments",
                  "description",
                  "input_types",
                  "output_types",
                  "category",
                  'enabled',
                  'interactive')
