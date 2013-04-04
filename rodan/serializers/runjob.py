from rodan.models.runjob import RunJob
from rodan.models.result import Result
from rest_framework import serializers


class ResultRunJobSerializer(serializers.HyperlinkedModelSerializer):
    """
        We define a simple serializer here to avoid a circular import
        with the 'normal' ResultSerializer.
    """
    class Meta:
        model = Result


class RunJobSerializer(serializers.HyperlinkedModelSerializer):
    sequence = serializers.Field(source='sequence')
    job_settings = serializers.CharField()
    # result = ResultSerializer()
    result = ResultRunJobSerializer()

    class Meta:
        model = RunJob
        read_only_fields = ("created", "updated")
        fields = ('url',
                  'workflow_run',
                  'workflow_job',
                  'sequence',
                  'result',
                  'page',
                  'job_settings',
                  'needs_input')
