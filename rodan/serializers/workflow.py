from rodan.models.workflow import Workflow
from rest_framework import serializers
from rodan.serializers.page import PageSerializer


class WorkflowSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.HyperlinkedRelatedField(view_name="project-detail")
    pages = PageSerializer()

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
