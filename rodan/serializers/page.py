from rodan.models.page import Page
from rest_framework import serializers


class PageSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.HyperlinkedRelatedField(view_name="project-detail")
    page_image = serializers.FileField()
    page_order = serializers.IntegerField()
    image_file_size = serializers.IntegerField()

    small_thumb_url = serializers.Field(source='small_thumb_url')
    medium_thumb_url = serializers.Field(source='medium_thumb_url')
    large_thumb_url = serializers.Field(source='large_thumb_url')

    class Meta:
        model = Page
        read_only_fields = ('created', 'updated')
        fields = ("url", "project", "page_image", "image_file_size", "small_thumb_url", "medium_thumb_url", "large_thumb_url", "page_order", "created", "updated")
