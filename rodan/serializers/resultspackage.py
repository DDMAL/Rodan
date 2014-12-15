from rodan.models import ResultsPackage, OutputPort
from rest_framework import serializers
from rodan.serializers import AbsoluteURLField

class ResultsPackageSerializer(serializers.HyperlinkedModelSerializer):
    package_url = AbsoluteURLField(source="package_relurl", read_only=True)

    class Meta:
        model = ResultsPackage
        fields = ('url',
                  'uuid',
                  'status',
                  'percent_completed',
                  'workflow_run',
                  'output_ports',
                  'creator',
                  'error_summary',
                  'error_details',
                  'created',
                  'updated',
                  'expiry_time',
                  'package_url')
        read_only_fields = ('creator', 'percent_completed', 'error_summary', 'error_details')

class ResultsPackageListSerializer(serializers.HyperlinkedModelSerializer):
    package_url = AbsoluteURLField(source="package_relurl", read_only=True)
    output_ports = serializers.HyperlinkedRelatedField(many=True, view_name='outputport-detail', required=False, queryset=OutputPort.objects.all())

    class Meta:
        model = ResultsPackage
        fields = ('url',
                  'uuid',
                  'status',
                  'percent_completed',
                  'workflow_run',
                  'output_ports',
                  'creator',
                  'error_summary',
                  'error_details',
                  'created',
                  'updated',
                  'expiry_time',
                  'package_url')
        read_only_fields = ('creator', 'percent_completed', 'error_summary', 'error_details')
    def validate(self, data):
        if 'output_ports' in data:
            # validate if outputports are in the WorkflowRun's Workflow
            wf = data['workflow_run'].workflow
            for op in data['output_ports']:
                if op.workflow_job.workflow != wf:
                    raise serializers.ValidationError("Confliction between WorkflowRun and OutputPort: OutputPort {0} not in WorkflowRun {1}'s Workflow.".format(op.uuid.hex, data['workflow_run'].uuid.hex))
        else:
            # set default OutputPorts
            wf = data['workflow_run'].workflow
            ops = OutputPort.objects.filter(workflow_job__workflow=wf, connections__isnull=True)
            data['output_ports'] = list(ops)
        return data
