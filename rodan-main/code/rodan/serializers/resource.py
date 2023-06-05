from rodan.serializers.resourcelabel import ResourceLabelSerializer
from rodan.models.resource import Resource
from rest_framework import serializers
# from rodan.serializers.user import UserListSerializer
from rodan.serializers import AbsoluteURLField


class HyperlinkedResourceSerializer(serializers.HyperlinkedModelSerializer):
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
        fields = "__all__"

class NestedLabelsResourceSerializer(HyperlinkedResourceSerializer):
    labels = ResourceLabelSerializer(many=True, read_only=True)
