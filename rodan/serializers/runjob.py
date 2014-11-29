from rodan.models.runjob import RunJob
from rest_framework import serializers
from rodan.serializers.resource import AbsoluteURLField

#class ResultRunJobSerializer(serializers.HyperlinkedModelSerializer):
#    """
#        We define a simple serializer here to avoid a circular import
#        with the 'normal' ResultSerializer.
#    """
#    small_thumb_url = serializers.Field(source="small_thumb_url")
#    medium_thumb_url = serializers.Field(source="medium_thumb_url")
#    result = serializers.Field(source="image_url")
#    run_job_name = serializers.Field(source="run_job_name")
#
#    class Meta:
#        model = Result


# class PageRunJobSerializer(serializers.HyperlinkedModelSerializer):
#     medium_thumb_url = serializers.Field(source="medium_thumb_url")
#     large_thumb_url = serializers.Field(source="medium_thumb_url")
#     uuid = serializers.Field(source='uuid')

#     class Meta:
#         model = Page
#         fields = ('url', 'uuid', 'name', 'page_order', 'medium_thumb_url', 'large_thumb_url')


class RunJobSerializer(serializers.HyperlinkedModelSerializer):
    job = serializers.HyperlinkedRelatedField(view_name='job-detail', source='job', read_only=True)
    job_name = serializers.Field(source='job_name')
    workflow = serializers.HyperlinkedRelatedField(view_name='workflow-detail', source='workflow', read_only=True)
    interactive = AbsoluteURLField(source='interactive')

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
                  'job_settings',
                  'needs_input',
                  'ready_for_input',
                  'status',
                  'created',
                  'updated',
                  'error_summary',
                  'error_details',
                  'interactive')
