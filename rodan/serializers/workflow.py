from rodan.models.workflow import Workflow
from rest_framework import serializers
from rodan.serializers.workflowjob import WorkflowJobSerializer
from rodan.serializers.workflowrun import WorkflowRunSerializer


class WorkflowSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.HyperlinkedRelatedField(view_name="project-detail")
    creator = serializers.HyperlinkedRelatedField(view_name="user-detail")
    uuid = serializers.Field(source='uuid')
    # runs = serializers.IntegerField(required=False)

    class Meta:
        model = Workflow
        read_only_fields = ('created', 'updated', 'workflow_jobs', 'workflow_runs')
        fields = ("url",
                  "uuid",
                  "name",
                  "project",
                  "workflow_jobs",
                  "description",
                  "created",
                  "updated",
                  "valid",
                  "workflow_runs")


class WorkflowListSerializer(serializers.HyperlinkedModelSerializer):
    uuid = serializers.Field(source='uuid')
    project = serializers.HyperlinkedRelatedField(view_name="project-detail")
    creator = serializers.HyperlinkedRelatedField(view_name="user-detail")

    class Meta:
        model = Workflow
        read_only_fields = ('created', 'updated')
        fields = ('url',
                  "uuid",
                  'project',
                  'creator',
                  'uuid',
                  'name',
                  'valid',
                  'created',
                  'updated')
