from rodan.models.resource import Resource
from rest_framework import serializers
from rodan.serializers.user import UserListSerializer

class AbsoluteURLField(serializers.Field):
    def to_native(self, relative_url):
        """
        http://www.django-rest-framework.org/api-guide/fields/
        """
        if relative_url is not None:
            request = self.context['request']
            return request.build_absolute_uri(relative_url)
        else:
            return super(AbsoluteURLField, self).to_native(relative_url)


class ResourceSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.HyperlinkedRelatedField(view_name="project-detail")
    creator = UserListSerializer(read_only=True)
    resource_file = AbsoluteURLField(source='resource_url')
    compat_resource_file = AbsoluteURLField(source='compat_file_url')
    resource_type = serializers.HyperlinkedRelatedField(view_name="resourcetype-detail")
    small_thumb = AbsoluteURLField(source='small_thumb_url')
    medium_thumb = AbsoluteURLField(source='medium_thumb_url')
    large_thumb = AbsoluteURLField(source='large_thumb_url')

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
                  "updated",
                  "small_thumb",
                  "medium_thumb",
                  "large_thumb")


class OutputResourceSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Resource
