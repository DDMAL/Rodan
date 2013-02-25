from rodan.models.workflowjob import WorkflowJob
from rest_framework import serializers


class WorkflowJobSerializer(serializers.HyperlinkedModelSerializer):
    workflow = serializers.HyperlinkedRelatedField(view_name="workflow-detail")
    job = serializers.HyperlinkedRelatedField(view_name="job-detail")
    sequence = serializers.IntegerField(required=False)
    job_settings = serializers.CharField(required=False)
    needs_input = serializers.BooleanField(required=False)
    job_type = serializers.IntegerField(required=False)

    name = serializers.Field(source="name")
    input_pixel_types = serializers.Field(source="input_pixel_types")
    output_pixel_types = serializers.Field(source="output_pixel_types")

    class Meta:
        model = WorkflowJob
        read_only_fields = ('created', 'updated')
        fields = ("url",
                "workflow",
                "input_pixel_types",
                "output_pixel_types",
                "name",
                "job",
                "job_type",
                "needs_input",
                "sequence",
                "job_settings",
                "created",
                "updated")
