from rodan.models.runjob import RunJob
from rest_framework import serializers


class RunJobSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RunJob
        read_only_fields = ("created", "updated")
        fields = ('url',
                  'workflow_run',
                  'workflow_job',
                  'page',
                  'job_settings',
                  'needs_input')
