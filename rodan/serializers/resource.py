from rodan.models.resource import Resource
from rest_framework import serializers
from rodan.serializers.user import UserListSerializer
from rodan.serializers import AbsoluteURLField


class ResourceSerializer(serializers.HyperlinkedModelSerializer):
    uuid = serializers.CharField(read_only=True)
    creator = serializers.SlugRelatedField(slug_field="username", read_only=True)
    resource_file = AbsoluteURLField(source="resource_url", read_only=True)
    # compat_resource_file = AbsoluteURLField(source='compat_file_url', read_only=True)
    small_thumb = AbsoluteURLField(source="small_thumb_url", read_only=True)
    medium_thumb = AbsoluteURLField(source="medium_thumb_url", read_only=True)
    large_thumb = AbsoluteURLField(source="large_thumb_url", read_only=True)
    viewer_url = AbsoluteURLField(source="viewer_relurl", read_only=True)

    class Meta:
        model = Resource
        read_only_fields = (
            "url"
            "uuid"
            "created",
            "updated",
            "processing_status",
            "error_summary",
            "error_details",
            "origin",
            "has_thumb",
        )  # The only updatable fields are: name, resource_type
        fields = (
            "url",
            "uuid",
            "name",
            "description",
            "project",
            "resource_file",
            "resource_type",
            "processing_status",
            "error_summary",
            "error_details",
            "creator",
            "origin",
            "created",
            "updated",
            "resource_file_path",
            "viewer_url",
            "large_thumb",
            "medium_thumb",
            "small_thumb",
        )
