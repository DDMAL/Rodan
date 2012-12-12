from rodan.models.workflow import Workflow
from rest_framework import serializers


class WorkflowSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.HyperlinkedRelatedField(view_name="project-detail")
    jobs = serializers.ManyHyperlinkedRelatedField(view_name="workflowjob-detail")
    pages = serializers.ManyHyperlinkedRelatedField(view_name="page-detail")

    class Meta:
        model = Workflow
        read_only_fields = ('created', 'updated')
        fields = ("url",
                  "project",
                  "jobs",
                  "pages",
                  "description",
                  "has_started",
                  "created",
                  "updated")
