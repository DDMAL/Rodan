from rodan.models.runjob import RunJob
from rest_framework import serializers
from rodan.serializers import AbsoluteURLField


class RunJobSerializer(serializers.HyperlinkedModelSerializer):
    job = serializers.HyperlinkedRelatedField(view_name='job-detail', read_only=True)
    interactive_url = AbsoluteURLField(read_only=True, source="interactive_relurl")

    class Meta:
        model = RunJob
        read_only_fields = ("created", "updated")
        fields = ('url',
                  'uuid',
                  'job',
                  'job_name',
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
                  'interactive_url')
