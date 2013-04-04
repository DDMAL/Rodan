from rodan.models.page import Page
from rest_framework import serializers
from rodan.serializers.user import UserSerializer


class PageSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.HyperlinkedRelatedField(view_name="project-detail")
    page_image = serializers.FileField()
    page_order = serializers.IntegerField()
    # image_file_size = serializers.IntegerField()
    creator = UserSerializer()

    image_file_size = serializers.Field(source="image_file_size")
    compat_image_file_size = serializers.Field(source="compat_image_file_size")
    small_thumb_url = serializers.Field(source='small_thumb_url')
    medium_thumb_url = serializers.Field(source='medium_thumb_url')
    large_thumb_url = serializers.Field(source='large_thumb_url')

    class Meta:
        model = Page
        read_only_fields = ('created', 'updated')
        fields = ("url",
                  "project",
                  "name",
                  "page_image",
                  "creator",
                  "image_file_size",
                  "compat_image_file_size",
                  "small_thumb_url",
                  "medium_thumb_url",
                  "large_thumb_url",
                  "page_order",
                  "created",
                  "updated")


class MinimalPageSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.HyperlinkedRelatedField(view_name="project-detail")
    page_image = serializers.FileField()
    page_order = serializers.IntegerField()

    image_file_size = serializers.Field(source="image_file_size")
    compat_image_file_size = serializers.Field(source="compat_image_file_size")
    small_thumb_url = serializers.Field(source='small_thumb_url')
    medium_thumb_url = serializers.Field(source='medium_thumb_url')
    large_thumb_url = serializers.Field(source='large_thumb_url')

    class Meta:
        model = Page
        read_only_fields = ('created', 'updated')
        fields = ("url",
                  "project",
                  "name",
                  "page_image",
                  "creator",
                  "image_file_size",
                  "compat_image_file_size",
                  "small_thumb_url",
                  "medium_thumb_url",
                  "large_thumb_url",
                  "page_order",
                  "created",
                  "updated")
