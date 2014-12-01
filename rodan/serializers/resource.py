from rodan.models.resource import Resource
from rest_framework import serializers
from rodan.serializers.user import UserListSerializer

class AbsoluteURLField(serializers.Field):
    def to_representation(self, relative_url):
        """
        http://www.django-rest-framework.org/api-guide/fields/
        """
        if relative_url is not None:
            request = self.context['request']
            return request.build_absolute_uri(relative_url)
        else:
            return None


class ResourceSerializer(serializers.HyperlinkedModelSerializer):
    creator = UserListSerializer(read_only=True)
    resource_file = AbsoluteURLField(source='resource_url', read_only=True)
    compat_resource_file = AbsoluteURLField(source='compat_file_url', read_only=True)
    small_thumb = AbsoluteURLField(source='small_thumb_url', read_only=True)
    medium_thumb = AbsoluteURLField(source='medium_thumb_url', read_only=True)
    large_thumb = AbsoluteURLField(source='large_thumb_url', read_only=True)

    class Meta:
        model = Resource
        read_only_fields = ('created', 'updated', 'error_summary', 'error_details', 'processing_status', 'origin', 'has_thumb')
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
                  "updated",
                  "has_thumb",
                  "small_thumb",
                  "medium_thumb",
                  "large_thumb")
