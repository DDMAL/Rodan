from rodan.models.workflowrun import WorkflowRun
from rest_framework import serializers


class WorkflowRunSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WorkflowRun
        read_only_fields = ("created", "updated", 'creator', 'project', 'workflow_name')
        extra_kwargs = {
            'workflow': {'allow_null': False, 'required': True}
        }
        fields = ('url',
                  'uuid',
                  'project',
                  'workflow',
                  'workflow_name',
                  'created',
                  'updated',
                  'test_run',
                  'creator',
                  'status')


class WorkflowRunByPageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WorkflowRun
        read_only_fields = ("created", "updated", 'creator', 'project', 'workflow_name')
        extra_kwargs = {
            'workflow': {'allow_null': False, 'required': True}
        }
        fields = ('url',
                  'uuid',
                  'project',
                  'workflow',
                  'workflow_name',
                  'created',
                  'updated',
                  'test_run',
                  'creator')
