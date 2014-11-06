from rodan.models.resource import Resource
from rest_framework import serializers
from rodan.serializers.user import UserListSerializer


class ResourceSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.HyperlinkedRelatedField(view_name="project-detail")
    creator = UserListSerializer(read_only=True)
    uuid = serializers.Field(source='uuid')
    resource_file = serializers.Field(source='resource_url')
    compat_resource_file = serializers.Field(source='compat_file_url')
    resource_type = serializers.HyperlinkedRelatedField(view_name="resourcetype-detail")

    class Meta:
        model = Resource
        read_only_fields = ('created', 'updated', 'error_summary', 'error_details', 'processing_status', 'origin')
        fields = ("url",
                  "uuid",
                  "project",
                  "name",
                  "resource_type",
                  "resource_file",
                  "compat_resource_file",
                  "processing_status",
                  "error_summary",
                  "error_details",
                  "creator",
                  "origin",
                  "created",
                  "updated")


class OutputResourceSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Resource
