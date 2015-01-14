from rodan.models.runjob import RunJob
from rest_framework import serializers
from rodan.serializers import AbsoluteURLField, TransparentField


class RunJobSerializer(serializers.HyperlinkedModelSerializer):
    job = serializers.HyperlinkedRelatedField(view_name='job-detail', read_only=True)
    interactive_url = AbsoluteURLField(read_only=True, source="interactive_relurl")
    job_settings = TransparentField(required=False)

    class Meta:
        model = RunJob
        read_only_fields = ("created", "updated")
        fields = ('url',
                  'uuid',
                  'job',
                  'job_name',
                  'workflow_run',
                  'workflow_job',
                  'workflow_job_uuid',
                  'resource_uuid',
                  'inputs',
                  'outputs',
                  'job_settings',
                  'status',
                  'created',
                  'updated',
                  'error_summary',
                  'error_details',
                  'interactive_url')
