from rodan.models.workflowrun import WorkflowRun
from rest_framework import serializers
from rodan.serializers.runjob import RunJobSerializer


class WorkflowRunSerializer(serializers.HyperlinkedModelSerializer):
    run_jobs = RunJobSerializer()
    creator = serializers.HyperlinkedRelatedField(view_name="user-detail")

    class Meta:
        model = WorkflowRun
        read_only_fields = ("created", "updated")
        fields = ('url',
                  'run_jobs',
                  'workflow',
                  'run',
                  'created',
                  'updated',
                  'test_run',
                  'creator')


class WorkflowRunByPageSerializer(serializers.HyperlinkedModelSerializer):
    creator = serializers.HyperlinkedRelatedField(view_name="user-detail")

    class Meta:
        model = WorkflowRun
        read_only_fields = ("created", "updated")
        fields = ('url',
                  'workflow',
                  'run',
                  'created',
                  'updated',
                  'test_run',
                  'creator')
