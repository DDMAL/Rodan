from rodan.models.runjob import RunJob
from rest_framework import serializers
from rodan.serializers.resource import AbsoluteURLField


class RunJobSerializer(serializers.HyperlinkedModelSerializer):
    job = serializers.HyperlinkedRelatedField(view_name='job-detail', read_only=True)
    job_name = serializers.CharField(read_only=True)
    workflow = serializers.HyperlinkedRelatedField(view_name='workflow-detail', read_only=True)
    interactive = AbsoluteURLField(read_only=True)

    class Meta:
        model = RunJob
        read_only_fields = ("created", "updated")
        fields = ('url',
                  'uuid',
                  'job',
                  'job_name',
                  'workflow',
                  'workflow_run',
                  'workflow_job',
                  'inputs',
                  'outputs',
                  'job_settings', # [TODO] replace with a JSON serializer
                  'ready_for_input',
                  'status',
                  'created',
                  'updated',
                  'error_summary',
                  'error_details',
                  'interactive')
