from rodan.models.workflowjob import WorkflowJob
from rodan.serializers.inputport import InputPortSerializer
from rodan.serializers.outputport import OutputPortSerializer
from rodan.serializers import TransparentField

from rest_framework import serializers


class WorkflowJobSerializer(serializers.HyperlinkedModelSerializer):
    job_settings = TransparentField(required=False)
    input_ports = InputPortSerializer(many=True, read_only=True)
    output_ports = OutputPortSerializer(many=True, read_only=True)

    class Meta:
        model = WorkflowJob
        read_only_fields = (
            "created",
            "updated",
            "input_ports",
            "output_ports",
            "group",
        )  # group is read only. To set group, use workflowjobgroup view.
        fields = (
            "url",
            "uuid",
            "workflow",
            "input_ports",
            "output_ports",
            "job_name",
            "job_description",
            "job",
            "job_settings",
            "name",
            "group",
            "created",
            "updated",
        )
