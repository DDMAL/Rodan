from rodan.models.workflowrun import WorkflowRun
from rest_framework import serializers
from rodan.serializers.runjob import RunJobSerializer


class WorkflowRunSerializer(serializers.HyperlinkedModelSerializer):
    run_jobs = RunJobSerializer()

    class Meta:
        model = WorkflowRun
        read_only_fields = ("created", "updated")
        fields = ('url',
                  'run_jobs',
                  'workflow',
                  'run')
