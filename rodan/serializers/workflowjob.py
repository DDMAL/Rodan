from rodan.models.workflowjob import WorkflowJob
from rodan.models.inputport import InputPort
from rodan.models.outputport import OutputPort
from rodan.serializers.inputport import InputPortSerializer
from rodan.serializers.outputport import OutputPortSerializer
from rodan.serializers import TransparentField

from rest_framework import serializers

class WorkflowJobSerializer(serializers.HyperlinkedModelSerializer):
    job_settings = TransparentField(required=False)

    class Meta:
        model = WorkflowJob
        read_only_fields = ('created', 'updated', 'input_ports', 'output_ports')
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
