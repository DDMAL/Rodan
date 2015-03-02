from rodan.models.workflowrun import WorkflowRun
from rest_framework import serializers


class WorkflowRunSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WorkflowRun
        read_only_fields = ("created", "updated", 'creator', 'project')
        extra_kwargs = {
            'workflow': {'allow_null': False, 'required': True}
        }
        fields = ('url',
                  'uuid',
                  'project',
                  'workflow',
                  'created',
                  'updated',
                  'creator',
                  'status',
                  'name',
                  'description')


class WorkflowRunByPageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WorkflowRun
        read_only_fields = ("created", "updated", 'creator', 'project')
        extra_kwargs = {
            'workflow': {'allow_null': False, 'required': True}
        }
        fields = ('url',
                  'uuid',
                  'project',
                  'workflow',
                  'created',
                  'updated',
                  'creator',
                  'status',
                  'name',
                  'description')
