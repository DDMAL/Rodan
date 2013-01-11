from rodan.models.workflowjob import WorkflowJob
from rest_framework import serializers


class WorkflowJobSerializer(serializers.ModelSerializer):
    workflow = serializers.HyperlinkedRelatedField(view_name="workflow-detail")
    job = serializers.HyperlinkedRelatedField(view_name="job-detail")

    class Meta:
        model = WorkflowJob
        read_only_fields = ('created', 'updated')
        fields = ("workflow", "job", "sequence", "job_settings", "created", "updated")
