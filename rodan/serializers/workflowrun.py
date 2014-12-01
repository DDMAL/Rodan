from rodan.models.workflowrun import WorkflowRun
from rest_framework import serializers


class WorkflowRunSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WorkflowRun
        read_only_fields = ("created", "updated", 'creator')
        fields = ('url',
                  'uuid',
                  'workflow',
                  'created',
                  'updated',
                  'test_run',
                  'creator',
                  'status')


class WorkflowRunByPageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WorkflowRun
        read_only_fields = ("created", "updated")
        fields = ('url',
                  'uuid',
                  'workflow',
                  'created',
                  'updated',
                  'test_run',
                  'creator')
