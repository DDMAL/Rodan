from rodan.models.workflow import Workflow
from rest_framework import serializers
from rodan.serializers.workflowjob import WorkflowJobSerializer
from rodan.serializers.workflowrun import WorkflowRunSerializer


class WorkflowSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Workflow
        read_only_fields = ('creator', 'created', 'updated', 'workflow_jobs', 'workflow_runs')
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
    class Meta:
        model = Workflow
        read_only_fields = ('creator', 'created', 'updated')
        fields = ('url',
                  "uuid",
                  'project',
                  'creator',
                  'uuid',
                  'name',
                  'valid',
                  'created',
                  'updated')
