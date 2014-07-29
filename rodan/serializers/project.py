from rodan.models.project import Project
from rest_framework import serializers


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    creator = serializers.HyperlinkedRelatedField(view_name="user-detail")
    uuid = serializers.Field(source="uuid")

    class Meta:
        model = Project
        read_only_fields = ('created', 'updated')
        fields = ("uuid", "url", "name", "description", "creator")


class ProjectListSerializer(serializers.HyperlinkedModelSerializer):
    workflow_count = serializers.Field(source="workflow_count")

    class Meta:
        model = Project
        read_only_fields = ('created', 'updated')
        fields = ('url',
                  'uuid',
                  'name',
                  "workflow_count",
                  'description',
                  'creator',
                  'created',
                  'updated')
