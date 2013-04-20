from rodan.models.project import Project
from rest_framework import serializers
from rodan.serializers.page import MinimalPageSerializer
from rodan.serializers.workflow import WorkflowSerializer
from rodan.serializers.user import UserListSerializer


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    # creator = serializers.HyperlinkedRelatedField(view_name="user-detail")
    creator = UserListSerializer()
    pages = MinimalPageSerializer(many=True, required=False, read_only=True)
    workflows = WorkflowSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = Project
        read_only_fields = ('created', 'updated')
        fields = ("url", "name", "description", "creator", "pages", "workflows")


class ProjectListSerializer(serializers.HyperlinkedModelSerializer):
    page_count = serializers.Field(source="page_count")
    workflow_count = serializers.Field(source="workflow_count")
    creator = UserListSerializer()

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
