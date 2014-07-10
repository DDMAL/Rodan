from rodan.models.workflowjob import WorkflowJob
from rest_framework import serializers


class WorkflowJobSerializer(serializers.HyperlinkedModelSerializer):
    workflow = serializers.HyperlinkedRelatedField(view_name="workflow-detail", required=False)
    job = serializers.HyperlinkedRelatedField(view_name="job-detail")
    sequence = serializers.IntegerField(required=False)
    job_settings = serializers.CharField(required=False)  # this actually sends it as a JSON object
    job_type = serializers.IntegerField(required=False)

    job_name = serializers.Field(source="job_name")
    job_description = serializers.Field(source="job_description")
    input_pixel_types = serializers.Field(source="input_pixel_types")
    output_pixel_types = serializers.Field(source="output_pixel_types")
    input_ports = serializers.Field(source="input_ports")
    output_ports = serializers.Field(source="output_ports")

    class Meta:
        model = WorkflowJob
        read_only_fields = ('created', 'updated')
        fields = ("url",
                  "workflow",
                  "input_pixel_types",
                  "output_pixel_types",
                  "input_ports",
                  "output_ports",
                  "job_name",
                  "job_description",
                  "job_type",
                  "job",
                  "sequence",
                  "job_settings",
                  "created",
                  "updated")
