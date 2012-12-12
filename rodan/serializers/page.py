from rodan.models.page import Page
from rest_framework import serializers


class PageSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.HyperlinkedRelatedField(view_name="project-detail")
    page_image = serializers.FileField()
    page_order = serializers.IntegerField()

    class Meta:
        model = Page
        read_only_fields = ('created', 'updated')
        fields = ("url", "project", "page_image", "page_order", "created", "updated")


class PageModelSerializer(serializers.ModelSerializer):
    # project = serializers.HyperlinkedRelatedField(view_name="project-detail")
    page_image = serializers.FileField()
    page_order = serializers.IntegerField()

    class Meta:
        model = Page
        read_only_fields = ('created', 'updated')
        fields = ("page_image", "page_order", "created", "updated")
