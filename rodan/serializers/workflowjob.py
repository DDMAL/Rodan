from rodan.models.workflowjob import WorkflowJob
from rodan.models.inputport import InputPort
from rodan.models.outputport import OutputPort
from rodan.serializers.inputport import InputPortSerializer
from rodan.serializers.outputport import OutputPortSerializer
from rest_framework import serializers


class WorkflowJobSerializer(serializers.HyperlinkedModelSerializer):
    workflow = serializers.HyperlinkedRelatedField(view_name="workflow-detail", required=False)
    job = serializers.HyperlinkedRelatedField(view_name="job-detail")
    job_settings = serializers.CharField(required=False)  # this actually sends it as a JSON object

    job_name = serializers.Field(source="job_name")
    job_description = serializers.Field(source="job_description")

    class Meta:
        model = WorkflowJob
        read_only_fields = ('created', 'updated')
        fields = ("url",
                  "uuid",
                  "workflow",
                  "input_ports",
                  "output_ports",
                  "job_name",
                  "job_description",
                  "job",
                  "job_settings",
                  "created",
                  "updated")
