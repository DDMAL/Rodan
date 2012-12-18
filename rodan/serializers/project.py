from rodan.models.project import Project
from rest_framework import serializers
from rodan.serializers.page import PageSerializer
from rodan.serializers.workflow import WorkflowSerializer


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    creator = serializers.HyperlinkedRelatedField(view_name="user-detail")
    pages = PageSerializer()
    workflows = WorkflowSerializer()

    class Meta:
        model = Project
        fields = ("url", "name", "description", "creator", "pages", "workflows")
