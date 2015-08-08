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
                  "name",
                  "group",
                  "created",
                  "updated")

    def validate(self, data):
        if 'group' in data and data['group']:
            g = data['group']
            g_wf = g.workflow_jobs.first()
            if g_wf:
                wf = data.get('workflow', self.instance.workflow)
                if wf.uuid != g_wf.uuid:
                    raise serializers.ValidationError({"group": ["The assigned group does not belong to the Workflow of this WorkflowJob."]})
        return data
