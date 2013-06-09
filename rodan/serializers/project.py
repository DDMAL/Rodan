from rodan.models.project import Project
from rest_framework import serializers
from rodan.serializers.page import MinimalPageSerializer
from rodan.serializers.workflow import WorkflowSerializer


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    # creator = serializers.HyperlinkedRelatedField(view_name="user-detail")
    creator = serializers.HyperlinkedRelatedField(view_name="user-detail")
    pages = MinimalPageSerializer(many=True, required=False, read_only=True)
    workflows = WorkflowSerializer(many=True, required=False, read_only=True)
    uuid = serializers.Field(source="uuid")

    class Meta:
        model = Project
        read_only_fields = ('created', 'updated')
        fields = ("uuid", "url", "name", "description", "creator", "pages", "workflows")


class ProjectListSerializer(serializers.HyperlinkedModelSerializer):
    page_count = serializers.Field(source="page_count")
    workflow_count = serializers.Field(source="workflow_count")

    class Meta:
        model = Project
        read_only_fields = ('created', 'updated')
        fields = ('url',
                  'name',
                  "page_count",
                  "workflow_count",
                  'description',
                  'creator',
                  'created',
                  'updated')
