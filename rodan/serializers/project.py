from rodan.models.project import Project
from rest_framework import serializers
from rodan.serializers.page import PageSerializer
from rodan.serializers.workflow import WorkflowSerializer


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    creator = serializers.HyperlinkedRelatedField(view_name="user-detail")
    # pages = serializers.RelatedField()
    # workflows = serializers.RelatedField()
    pages = PageSerializer(many=True, required=False, read_only=True)
    workflows = WorkflowSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = Project
        read_only_fields = ('created', 'updated')
        fields = ("url", "name", "description", "creator", "pages", "workflows")
