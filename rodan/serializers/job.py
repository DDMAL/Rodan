from rest_framework import serializers
from rodan.models.job import Job

# this takes care of making sure all the jobs are
# initialized.
from rodan import jobs


class JobSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Job
        fields = ("url", "name", "arguments", "input_types", "output_types", "category", 'is_enabled', 'is_automatic', 'is_required')
