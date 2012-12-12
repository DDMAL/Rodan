from rodan.models.project import Project
from rest_framework import serializers


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    creator = serializers.HyperlinkedRelatedField(view_name="user-detail")
    pages = serializers.ManyHyperlinkedRelatedField(view_name="page-detail")
    workflows = serializers.ManyHyperlinkedRelatedField(view_name="workflow-detail")

    class Meta:
        model = Project
        fields = ("url", "name", "description", "creator", "pages", "workflows")
