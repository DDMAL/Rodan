from rodan.models.runjob import RunJob
from rest_framework import serializers
from rodan.serializers import AbsoluteURLField, TransparentField
from rodan.constants import task_status
from django.core.urlresolvers import reverse


class RunJobSerializer(serializers.HyperlinkedModelSerializer):
    job = serializers.HyperlinkedRelatedField(view_name='job-detail', read_only=True, lookup_field="uuid", lookup_url_kwarg="pk")
    job_settings = TransparentField(required=False)
    project = serializers.HyperlinkedRelatedField(view_name='project-detail', read_only=True, lookup_field="uuid", lookup_url_kwarg="pk")
    interactive_acquire = serializers.SerializerMethodField()

    def get_interactive_acquire(self, obj):
        if obj.status is task_status.WAITING_FOR_INPUT:
            relative_url = reverse('interactive-acquire', kwargs={'run_job_uuid': obj.pk})
            request = self.context['request']
            return request.build_absolute_uri(relative_url)
        else:
            return None

    class Meta:
        model = RunJob
        fields = ('url',
                  'uuid',
                  'job',
                  'job_name',
                  'workflow_run',
                  'project',
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
                  'working_user',
                  'working_user_expiry',
                  'interactive_acquire'
        )
