from rest_framework import serializers
from rodan.models.job import Job


class JobSerializer(serializers.HyperlinkedModelSerializer):
    settings = serializers.CharField(required=False)  # this actually sends it as JSON

    class Meta:
        model = Job
        fields = ("url",
                  "job_name",
                  "settings",
                  "description",
                  "category",
                  'enabled',
                  'interactive')
