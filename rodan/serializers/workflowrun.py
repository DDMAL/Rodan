from rodan.models.workflowrun import WorkflowRun
from rest_framework import serializers


class WorkflowRunSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WorkflowRun
        read_only_fields = ("created", "updated")
        fields = ('url',
                  'workflow',
                  'run')
