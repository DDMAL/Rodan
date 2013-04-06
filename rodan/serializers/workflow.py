from rodan.models.workflow import Workflow
from rest_framework import serializers
from rodan.serializers.page import MinimalPageSerializer
from rodan.serializers.workflowjob import WorkflowJobSerializer
from rodan.serializers.workflowrun import WorkflowRunSerializer


class WorkflowSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.HyperlinkedRelatedField(view_name="project-detail")
    pages = MinimalPageSerializer()
    workflow_jobs = WorkflowJobSerializer()
    workflow_runs = WorkflowRunSerializer()
    uuid = serializers.Field(source='uuid')

    class Meta:
        model = Workflow
        read_only_fields = ('created', 'updated')
        fields = ("url",
                  "uuid",
                  "name",
                  "project",
                  'runs',
                  "pages",
                  "workflow_jobs",
                  "description",
                  "has_started",
                  "created",
                  "updated",
                  "workflow_runs")
