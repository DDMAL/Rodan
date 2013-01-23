from rodan.models.result import Result
from rest_framework import serializers
from rodan.serializers.page import PageSerializer
from rodan.serializers.workflowjob import WorkflowJobSerializer


class ResultSerializer(serializers.HyperlinkedModelSerializer):
    page = PageSerializer()
    workflow_job = WorkflowJobSerializer()
    result = serializers.FileField()

    class Meta:
        model = Result
        fields = ("url", "page", "workflow_job", "task_name", "result", "created", "updated")
