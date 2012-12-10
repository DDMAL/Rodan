from rodan.models.page import Page
from rest_framework import serializers


class PageSerializer(serializers.HyperlinkedModelSerializer):
    project = serializers.HyperlinkedRelatedField(view_name="project-detail")

    class Meta:
        model = Page
        fields = ("url", "project", "page_image", "page_order", "created", "updated")
