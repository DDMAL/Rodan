from rodan.models.result import Result
from rest_framework import serializers
from rodan.serializers.workflowjob import WorkflowJobSerializer


class ResultSerializer(serializers.HyperlinkedModelSerializer):
    workflow_job = WorkflowJobSerializer()
    result = serializers.FileField(allow_empty_file=True)

    class Meta:
        model = Result
        fields = ("url", "result", "workflow_job", "task_name", "result", "created", "updated")
