from rest_framework import serializers
from rodan.models.job import Job

import rodan.jobs.gamera


class JobSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Job
        fields = ("url", "name", "arguments", "input_types", "output_types", "category")
